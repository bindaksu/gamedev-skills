# Kotlin Snippets: Play Services and Shell UI

Library versions as of 2026-10: Play Billing 9.x, PGS v2, Play Integrity standard requests, Play Asset Delivery. Signatures marked "verify" changed in recent majors; confirm against current release notes.

## 1. Play Billing 8+/9.x client

```kotlin
class BillingGateway(
    context: Context,
    private val server: PurchaseServer,          // POST token -> verify -> grant -> acknowledge/consume
    private val scope: CoroutineScope,
) : PurchasesUpdatedListener {

    private val client = BillingClient.newBuilder(context)
        .setListener(this)
        .enablePendingPurchases(
            PendingPurchasesParams.newBuilder().enableOneTimeProducts().build()  // no-arg form removed in PBL 8
        )
        .enableAutoServiceReconnection()                                        // PBL 8+
        .build()

    fun connect(onReady: () -> Unit) = client.startConnection(object : BillingClientStateListener {
        override fun onBillingSetupFinished(result: BillingResult) {
            if (result.responseCode == BillingClient.BillingResponseCode.OK) {
                onReady()
                recoverUnprocessed()
            }
            // BILLING_UNAVAILABLE in 9.x can mean system-blocked (e.g. OEM kids mode): show store as unavailable
        }
        override fun onBillingServiceDisconnected() { /* auto-reconnection handles retries */ }
    })

    fun queryProducts(ids: List<String>, onResult: (List<ProductDetails>) -> Unit) {
        val params = QueryProductDetailsParams.newBuilder()
            .setProductList(ids.map {
                QueryProductDetailsParams.Product.newBuilder()
                    .setProductId(it).setProductType(BillingClient.ProductType.INAPP).build()
            }).build()
        // PBL 8 listener returns a QueryProductDetailsResult with fetched and unfetched lists (verify)
        client.queryProductDetailsAsync(params) { billingResult, queryResult ->
            if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                onResult(queryResult.productDetailsList)
            }
        }
    }

    fun buy(activity: Activity, product: ProductDetails, accountHash: String) {
        val flow = BillingFlowParams.newBuilder()
            .setProductDetailsParamsList(listOf(
                BillingFlowParams.ProductDetailsParams.newBuilder().setProductDetails(product).build()
            ))
            .setObfuscatedAccountId(accountHash)   // hashed studio account ID, never raw PII
            .build()
        client.launchBillingFlow(activity, flow)
    }

    override fun onPurchasesUpdated(result: BillingResult, purchases: MutableList<Purchase>?) {
        if (result.responseCode != BillingClient.BillingResponseCode.OK) return
        purchases.orEmpty().forEach(::process)
    }

    private fun process(purchase: Purchase) {
        if (purchase.purchaseState != Purchase.PurchaseState.PURCHASED) return  // PENDING: wait
        scope.launch {
            // Server verifies via Play Developer API, grants idempotently by purchaseToken,
            // then acknowledges (non-consumable) or consumes (consumable). Unacknowledged
            // purchases are refunded after 3 days (verify window).
            server.verifyAndGrant(purchase.purchaseToken, purchase.products)
        }
    }

    private fun recoverUnprocessed() {
        val params = QueryPurchasesParams.newBuilder()
            .setProductType(BillingClient.ProductType.INAPP).build()
        client.queryPurchasesAsync(params) { _, list -> list.forEach(::process) }
    }
}
```

Server side outline:

```
POST /iap/google/grant { purchaseToken, productIds, accountHash }
1. Play Developer API: purchases.products (one-time) or purchases.subscriptionsv2 (subs) GET.
2. Check packageName, productId, purchaseState = purchased, obfuscatedExternalAccountId == accountHash.
3. INSERT grant keyed by purchaseToken (unique). Duplicate = return prior result.
4. Grant in the same DB transaction as the ledger write.
5. Consumable: consume (client consumeAsync or server API). Non-consumable: acknowledge server-side.
6. RTDN via Cloud Pub/Sub for refunds/voids; Voided Purchases API as backfill.
```

## 2. Play Games Services v2 sign-in

```kotlin
class GameApp : Application() {
    override fun onCreate() {
        super.onCreate()
        PlayGamesSdk.initialize(this)
    }
}

fun checkPgs(activity: Activity, onPlayer: (String?) -> Unit) {
    val signIn = PlayGames.getGamesSignInClient(activity)
    signIn.isAuthenticated.addOnCompleteListener { task ->
        val ok = task.isSuccessful && task.result.isAuthenticated
        if (!ok) { onPlayer(null); return@addOnCompleteListener }    // offer manual signIn() button later
        PlayGames.getPlayersClient(activity).currentPlayer
            .addOnSuccessListener { onPlayer(it.playerId) }
    }
}

// Link to your backend: one-time server auth code, exchanged server-side.
fun requestServerCode(activity: Activity, serverClientId: String, onCode: (String) -> Unit) {
    PlayGames.getGamesSignInClient(activity)
        .requestServerSideAccess(serverClientId, /* forceRefreshToken = */ false)
        .addOnSuccessListener(onCode)
}
```

PGS v2 identity is platform-level. For cross-platform accounts use Credential Manager (Sign in with Google) or your own login, then link the PGS player ID as one identity.

## 3. Play Integrity standard request

```kotlin
class IntegrityGate(context: Context, private val cloudProjectNumber: Long) {
    private val manager = IntegrityManagerFactory.createStandard(context)
    private var provider: StandardIntegrityManager.StandardIntegrityTokenProvider? = null

    fun warmUp() {   // once, at launch; preparation can take seconds
        manager.prepareIntegrityToken(
            StandardIntegrityManager.PrepareIntegrityTokenRequest.builder()
                .setCloudProjectNumber(cloudProjectNumber).build()
        ).addOnSuccessListener { provider = it }
    }

    /** requestHash: hash of the action payload (e.g. SHA-256 of "claim:reward42:nonce"). */
    fun token(requestHash: String, onToken: (String) -> Unit) {
        provider?.request(
            StandardIntegrityManager.StandardIntegrityTokenRequest.builder()
                .setRequestHash(requestHash).build()
        )?.addOnSuccessListener { onToken(it.token()) }
    }
}
```

The server decrypts the token through Google's endpoint, checks the request hash, and scores the verdict. Never decide locally.

## 4. Play Asset Delivery (fast-follow / on-demand)

```kotlin
class Packs(context: Context) {
    private val manager = AssetPackManagerFactory.getInstance(context)

    /** Never cache this path: the OS or user can move or delete fast-follow/on-demand packs. */
    fun pathOf(pack: String): String? = manager.getPackLocation(pack)?.assetsPath()

    fun ensure(pack: String, onReady: (String) -> Unit, onProgress: (Long, Long) -> Unit) {
        pathOf(pack)?.let { onReady(it); return }
        manager.registerListener { state ->
            if (state.name() != pack) return@registerListener
            when (state.status()) {
                AssetPackStatus.DOWNLOADING -> onProgress(state.bytesDownloaded(), state.totalBytesToDownload())
                AssetPackStatus.COMPLETED -> pathOf(pack)?.let(onReady)
                AssetPackStatus.WAITING_FOR_WIFI ->
                    manager.showConfirmationDialog(/* activityResultLauncher */)  // large download on cellular (verify signature)
                AssetPackStatus.FAILED -> { /* retry with backoff; show offline UI */ }
                else -> Unit
            }
        }
        manager.fetch(listOf(pack))
    }
}
```

## 5. Compose shell around the native surface

Two options. Prefer a separate Activity for heavy screens (shop, account, settings); use an overlay only for light UI. The overlay pattern is community practice, not an official recommendation; measure touch pass-through and frame impact.

```kotlin
// Option A: separate Activity for the store. The GameActivity pauses rendering in onPause.
class ShopActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { ShopScreen(onClose = ::finish) }
    }
}

// Option B: overlay a ComposeView on GameActivity, visible only while a panel is open.
class MainGameActivity : GameActivity() {
    private lateinit var overlay: ComposeView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        overlay = ComposeView(this).apply {
            visibility = View.GONE                   // GONE = touches reach the game surface
            setContent { InboxPanel(onClose = { hideOverlay() }) }
        }
        addContentView(overlay, ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
    }

    fun showOverlay() = runOnUiThread { overlay.visibility = View.VISIBLE }   // native pauses input
    fun hideOverlay() = runOnUiThread { overlay.visibility = View.GONE }
}
```

Never draw game-rate content in Compose; it runs on the main thread. Call `showOverlay` from native via a single JNI method, and have the native loop ignore touch while the overlay is visible.

## 6. Manifest essentials

```xml
<application
    android:appCategory="game">
    <activity
        android:name=".MainGameActivity"
        android:configChanges="orientation|screenSize|screenLayout|keyboardHidden|keyboard|density|uiMode|smallestScreenSize"
        android:exported="true">
        <meta-data android:name="android.app.lib_name" android:value="game" />
    </activity>
</application>
```

`appCategory="game"` is what exempts the game from API 36 large-screen resizability overrides. `configChanges` stops activity recreation (and surface loss) on rotation, fold, and density changes; handle them in native instead.
