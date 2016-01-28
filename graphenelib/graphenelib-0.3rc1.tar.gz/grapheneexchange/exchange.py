from grapheneapi.grapheneclient import GrapheneClient
from datetime import datetime
import time


class ExampleConfig() :
    """ The behavior of your program can be
        defined in a separated class (here called ``ExampleConfig()``. It
        contains the wallet and witness connection parameters:

        The config class is used to define several attributes *and*
        methods that will be used during API communication..


        **Additional Websocket Connections**:

        .. code-block:: python

            class Config(GrapheneWebsocketProtocol):  ## Note the dependency
                wallet_host           = "localhost"
                wallet_port           = 8092
                wallet_user           = ""
                wallet_password       = ""
                witness_url           = "ws://localhost:8090/"
                witness_user          = ""
                witness_password      = ""

        All methods within ``graphene.rpc`` are mapped to the
        corresponding RPC call of the wallet and the parameters are
        handed over directly. Similar behavior is implemented for
        ``graphene.ws`` which can deal with calls to the witness node.

        This allows the use of rpc commands similar to the
        ``GrapheneAPI`` class:

        .. code-block:: python

            graphene = GrapheneExchange(Config)
            # Calls to the cli-wallet
            print(graphene.rpc.info())
            print(graphene.rpc.get_account("init0"))
            print(graphene.rpc.get_asset("USD"))
            # Calls to the witness node
            print(ws.get_account_count())

    """

    #: Wallet connection parameters
    wallet_host           = "localhost"
    wallet_port           = 8092
    wallet_user           = ""
    wallet_password       = ""

    #: Witness connection parameter
    witness_url           = "ws://localhost:8090/"
    witness_user          = ""
    witness_password      = ""

    #: The account used here
    account               = "fabian"

    #: Markets to watch.
    watch_markets         = ["USD_BTS"]
    market_separator      = "_"


class GrapheneExchange(GrapheneClient) :
    """ This class serves as an abstraction layer for the decentralized
        exchange within the network and simplifies interaction for
        trading bots.

        :param config config: Configuration Class, similar to the
                              example above

        This class tries to map the poloniex API around the DEX but has
        some differences:

            * market pairs are denoted as 'quote'_'base', e.g. `USD_BTS`
            * Prices/Rates are denoted in 'base', i.e. the USD_BTS market
              is priced in BTS per USD.
              Example: in the USD_BTS market, a price of 300 means
              a USD is worth 300 BTS
            * All markets could be considered reversed as well ('BTS_USD')

        Usage:

        .. code-block:: python


            from grapheneexchange import GrapheneExchange
            import json


            class Config():
                wallet_host           = "localhost"
                wallet_port           = 8092
                wallet_user           = ""
                wallet_password       = ""
                witness_url           = "ws://10.0.0.16:8090/"
                witness_user          = ""
                witness_password      = ""

                watch_markets         = ["USD_BTS", "GOLD_BTS"]
                market_separator      = "_"
                account               = "mindphlux"

            if __name__ == '__main__':
                dex   = GrapheneExchange(Config)
                print(json.dumps(dex.returnTradeHistory("USD_BTS"),indent=4))
                print(json.dumps(dex.returnTicker(),indent=4))
                print(json.dumps(dex.return24Volume(),indent=4))
                print(json.dumps(dex.returnOrderBook("USD_BTS"),indent=4))
                print(json.dumps(dex.returnBalances(),indent=4))
                print(json.dumps(dex.returnOpenOrders("all"),indent=4))
                print(json.dumps(dex.buy("USD_BTS", 0.001, 10),indent=4))
                print(json.dumps(dex.sell("USD_BTS", 0.001, 10),indent=4))
    """
    markets = {}
    account = ""
    wallet = None

    def __init__(self, config, safe_mode=True) :
        self.safe_mode = safe_mode
        self.config = config
        super().__init__(config)

    def formatTimeFromNow(self, secs=0):
        """ Properly Format Time that is `x` seconds in the future

            :param int secs: Seconds to go in the future (`x>0`) or the
                             past (`x<0`)
            :return: Properly formated time for Graphene (`%Y-%m-%dT%H:%M:%S`)
            :rtype: str

        """
        return datetime.utcfromtimestamp(time.time() + int(secs)).strftime('%Y-%m-%dT%H:%M:%S')

    def _get_market_name_from_ids(self, quote_id, base_id,) :
        """ Returns the properly formated name of a market given base
            and quote ids

            :param str quote_id: Object ID of the quote asset
            :param str base_id: Object ID of the base asset
            :return: Market name with proper separator
            :rtype: str
        """
        quote, base  = self.ws.get_objects([quote_id, base_id])
        return quote["symbol"] + self.market_separator + quote["symbol"]

    def _get_assets_from_ids(self, base_id, quote_id) :
        """ Returns assets of a market given base
            and quote ids

            :param str quote_id: Object ID of the quote asset
            :param str base_id: Object ID of the base asset
            :return: object that contains `quote` and `base` asset objects
            :rtype: json
        """
        quote, base  = self.ws.get_objects([quote_id, base_id])
        return {"quote" : quote, "base" : base}

    def _get_asset_ids_from_name(self, market) :
        """ Returns the  base and quote ids given a properly formated
            market name

            :param str market: Market name (properly separated)
            :return: object that contains `quote` asset id and `base` asset id
            :rtype: json
        """
        quote_symbol, base_symbol = market.split(self.market_separator)
        quote  = self.rpc.get_asset(quote_symbol)
        base   = self.rpc.get_asset(quote_symbol)
        return {"quote" : quote["id"], "base" : base["id"]}

    def _get_assets_from_market(self, market) :
        """ Returns the  base and quote assets given a properly formated
            market name

            :param str market: Market name (properly separated)
            :return: object that contains `quote` and `base` asset objects
            :rtype: json
        """
        quote_symbol, base_symbol = market.split(self.market_separator)
        quote  = self.rpc.get_asset(quote_symbol)
        base   = self.rpc.get_asset(quote_symbol)
        return {"quote" : quote, "base" : base}

    def _get_price(self, o) :
        """ Given an object with `quote` and `base`, derive the correct
            price.

            :param Object o: Blockchain object that contains `quote` and `asset` amounts and asset ids.
            :return: price derived as `base`/`quote`

            Prices/Rates are denoted in 'base', i.e. the USD_BTS market
            is priced in BTS per USD.

            **Example:** in the USD_BTS market, a price of 300 means
            a USD is worth 300 BTS

            .. note::

                All prices returned are in the **reveresed** orientation as the
                market. I.e. in the BTC/BTS market, prices are BTS per BTS.
                That way you can multiply prices with `1.05` to get a +5%.
        """
        quote_amount = float(o["quote"]["amount"])
        base_amount  = float(o["base"]["amount"])
        quote_id     = o["quote"]["asset_id"]
        base_id      = o["base"]["asset_id"]
        quote, base  = self.ws.get_objects([quote_id, base_id])
        # invert price!
        return float((base_amount / 10 ** base["precision"]) /
                     (quote_amount / 10 ** quote["precision"]))

    def _get_price_filled(self, f, m):
        """ A filled order has `receives` and `pays` ops which serve as
            `base` and `quote` depending on sell or buy

            :param Object f: Blockchain object for filled orders
            :param str m: Market
            :return: Price

            Prices/Rates are denoted in 'base', i.e. the USD_BTS market
            is priced in BTS per USD.
            Example: in the USD_BTS market, a price of 300 means
            a USD is worth 300 BTS

            .. note::

                All prices returned are in the **reveresed** orientation as the
                market. I.e. in the BTC/BTS market, prices are BTS per BTS.
                That way you can multiply prices with `1.05` to get a +5%.

        """
        r = {}
        if f["op"]["receives"]["asset_id"] == m["base"] :
            # If the seller received "base" in a quote_base market, than
            # it has been a sell order of quote
            r["base"] = f["op"]["receives"]
            r["quote"] = f["op"]["pays"]
        else:
            # buy order
            r["base"] = f["op"]["pays"]
            r["quote"] = f["op"]["receives"]
        # invert price!
        return self._get_price(r)

    def _get_txorder_price(self, f, m):
        """ A newly place limit order has `amount_to_sell` and
            `min_to_receive` which serve as `base` and `quote` depending
            on sell or buy

            :param Object f: Blockchain object for historical orders
            :param str m: Market
            :return: Price
        """
        r = {}
        if f["min_to_receive"]["asset_id"] == m["base"] :
            # If the seller received "base" in a quote_base market, than
            # it has been a sell order of quote
            r["base"] = f["min_to_receive"]
            r["quote"] = f["amount_to_sell"]
        elif f["min_to_receive"]["asset_id"] == m["quote"]:
            # buy order
            r["base"] = f["amount_to_sell"]
            r["quote"] = f["min_to_receive"]
        else :
            return None
        # invert price!
        return self._get_price(r)

    def returnCurrencies(self):
        """ In contrast to poloniex, this call returns the assets of the
            watched markets only.

            Example Output:

            .. code-block:: json

            {'BTS': {'issuer': '1.2.3', 'id': '1.3.0', 'dynamic_asset_data_id': '2.3.0', 'precision': 5, 'symbol': 'BTS', 'options': {'max_market_fee': '1000000000000000', 'blacklist_authorities': [], 'blacklist_markets': [], 'description': '', 'whitelist_authorities': [], 'market_fee_percent': 0, 'core_exchange_rate': {'base': {'asset_id': '1.3.0', 'amount': 1}, 'quote': {'asset_id': '1.3.0', 'amount': 1}}, 'flags': 0, 'extensions': [], 'whitelist_markets': [], 'issuer_permissions': 0, 'max_supply': '360057050210207'}}, 'GOLD': {'issuer': '1.2.0', 'id': '1.3.106', 'dynamic_asset_data_id': '2.3.106', 'precision': 6, 'bitasset_data_id': '2.4.6', 'symbol': 'GOLD', 'options': {'max_market_fee': '1000000000000000', 'blacklist_authorities': [], 'blacklist_markets': [], 'description': '1 troy ounce .999 fine gold', 'whitelist_authorities': [], 'market_fee_percent': 0, 'core_exchange_rate': {'base': {'asset_id': '1.3.106', 'amount': 1}, 'quote': {'asset_id': '1.3.0', 'amount': 34145}}, 'flags': 128, 'extensions': [], 'whitelist_markets': [], 'issuer_permissions': 511, 'max_supply': '1000000000000000'}}, 'USD': {'issuer': '1.2.0', 'id': '1.3.121', 'dynamic_asset_data_id': '2.3.121', 'precision': 4, 'bitasset_data_id': '2.4.21', 'symbol': 'USD', 'options': {'max_market_fee': '1000000000000000', 'blacklist_authorities': [], 'blacklist_markets': [], 'description': '1 United States dollar', 'whitelist_authorities': [], 'market_fee_percent': 0, 'core_exchange_rate': {'base': {'asset_id': '1.3.121', 'amount': 5}, 'quote': {'asset_id': '1.3.0', 'amount': 15751}}, 'flags': 128, 'extensions': [], 'whitelist_markets': [], 'issuer_permissions': 511, 'max_supply': '1000000000000000'}}}

        """
        r = {}
        asset_ids = []
        for market in self.markets :
            m = self.markets[market]
            asset_ids.append(m["base"])
            asset_ids.append(m["quote"])
        asset_ids_unique = list(set(asset_ids))
        assets = self.ws.get_objects(asset_ids_unique)
        for a in assets:
            r.update({a["symbol"] : a})
        return r

    def returnFees(self) :
        """ Returns a dictionary of all fees that apply through the
            network

            Example output:

            .. code-block:: json

                {'proposal_create': {'fee': 400000.0},
                'asset_publish_feed': {'fee': 1000.0}, 'account_create':
                {'basic_fee': 950000.0, 'price_per_kbyte': 20000.0,
                'premium_fee': 40000000.0}, 'custom': {'fee': 20000.0},
                'asset_fund_fee_pool': {'fee': 20000.0},
                'override_transfer': {'fee': 400000.0}, 'fill_order':
                {}, 'asset_update': {'price_per_kbyte': 20000.0, 'fee':
                200000.0}, 'asset_update_feed_producers': {'fee':
                10000000.0}, 'assert': {'fee': 20000.0},
                'committee_member_create': {'fee': 100000000.0}}

        """
        from graphenebase.transactions import operations
        r = {}
        obj, base = self.ws.get_objects(["2.0.0", "1.3.0"])
        fees = obj["parameters"]["current_fees"]["parameters"]
        scale = float(obj["parameters"]["current_fees"]["scale"])
        for f in fees:
            op_name = "unkown %d" % f[0]
            for name in operations:
                if operations[name] == f[0]:
                    op_name = name
            fs = f[1]
            for _type in fs :
                fs[_type] = float(fs[_type]) * scale / 1e4 / 10 ** base["precision"]
            r[op_name] = fs
        return r

    def returnTicker(self):
        """ Returns the ticker for all markets.

            Output Parameters:

            * ``last``: Price of the order last filled
            * ``lowestAsk``: Price of the lowest ask
            * ``highestBid``: Price of the highest bid
            * ``baseVolume``: Volume of the base asset
            * ``quoteVolume``: Volume of the quote asset
            * ``percentChange``: 24h change percentage (in %)
            * ``settlement_price``: Settlement Price for borrow/settlement
            * ``core_exchange_rate``: Core exchange rate for payment of fee in non-BTS asset

            .. note::

                All prices returned by ``returnTicker`` are in the **reveresed**
                orientation as the market. I.e. in the BTC/BTS market, prices are
                BTS per BTS. That way you can multiply prices with `1.05` to
                get a +5%.

                The prices in a `quote`/`base` market is denoted in `base` per
                `quote`:

                    market: USD_BTS - price 300 BTS per USD

            Sample Output:

            .. code-block:: json

                {
                    "BTS_USD": {
                        "quoteVolume": 144.1862,
                        "settlement_price": 0.003009016674102742,
                        "lowestAsk": 0.002992220227408737,
                        "baseVolume": 48328.73333,
                        "percentChange": 2.0000000097901705,
                        "highestBid": 0.0029411764705882353,
                        "last": 0.003000000000287946,
                        "core_exchange_rate": 0.003161120960980772
                    },
                    "USD_BTS": {
                        "quoteVolume": 48328.73333,
                        "settlement_price": 332.3344827586207,
                        "lowestAsk": 340.0,
                        "baseVolume": 144.1862,
                        "percentChange": -1.9607843231354893,
                        "highestBid": 334.20000000000005,
                        "last": 333.33333330133934,
                        "core_exchange_rate": 316.3434782608696
                    }
                }

            .. note:: A market that has had no trades will result in
                      prices of "-1" to indicate that no trades have
                      happend.

        """
        r = {}
        for market in self.markets :
            m = self.markets[market]
            data = {}
            quote_asset, base_asset = self.ws.get_objects([m["quote"], m["base"]])
            marketHistory = self.ws.get_market_history(
                m["quote"], m["base"],
                24 * 60 * 60,
                self.formatTimeFromNow(-24 * 60 * 60),
                self.formatTimeFromNow(),
                api="history")
            orders = self.rpc.get_limit_orders(
                m["quote"], m["base"], 1)
            filled = self.ws.get_fill_order_history(
                m["quote"], m["base"], 0, api="history")
            # Price and ask/bids
            if filled :
                data["last"] = self._get_price_filled(filled[0], m)
            else :
                data["last"] = -1
            if len(orders) > 1:
                data["lowestAsk"]     = self._get_price(orders[1]["sell_price"])
                data["highestBid"]    = (1 / self._get_price(orders[0]["sell_price"]))
            else :
                data["lowestAsk"]     = -1
                data["highestBid"]    = -1
            # smartcoin stuff
            if "bitasset_data_id" in quote_asset :
                bitasset = self.ws.get_objects([quote_asset["bitasset_data_id"]])[0]
                backing_asset_id = bitasset["options"]["short_backing_asset"]
                if backing_asset_id == base_asset["id"]:
                    data["settlement_price"] = 1 / self._get_price(bitasset["current_feed"]["settlement_price"])
                    data["core_exchange_rate"] = 1 / self._get_price(bitasset["current_feed"]["core_exchange_rate"])
            elif "bitasset_data_id" in base_asset :
                bitasset = self.ws.get_objects([base_asset["bitasset_data_id"]])[0]
                backing_asset_id = bitasset["options"]["short_backing_asset"]
                if backing_asset_id == quote_asset["id"]:
                    data["settlement_price"] = self._get_price(bitasset["current_feed"]["settlement_price"])
                    data["core_exchange_rate"] = self._get_price(bitasset["current_feed"]["core_exchange_rate"])

            if len(marketHistory) :
                if marketHistory[0]["key"]["quote"] == m["quote"] :
                    data["baseVolume"]    = float(marketHistory[0]["base_volume"])  / (10 ** base_asset["precision"])
                    data["quoteVolume"]   = float(marketHistory[0]["quote_volume"]) / (10 ** quote_asset["precision"])
                    price24h = ((float(marketHistory[0]["open_quote"]) / 10 ** quote_asset["precision"]) /
                                (float(marketHistory[0]["open_base"])  / 10 ** base_asset["precision"]))
                else :
                    #: Looks weird but is correct:
                    data["baseVolume"]    = float(marketHistory[0]["quote_volume"]) / (10 ** base_asset["precision"])
                    data["quoteVolume"]   = float(marketHistory[0]["base_volume"])  / (10 ** quote_asset["precision"])
                    price24h = ((float(marketHistory[0]["open_base"])  / 10 ** quote_asset["precision"]) /
                                (float(marketHistory[0]["open_quote"]) / 10 ** base_asset["precision"]))
                data["percentChange"] = ((data["last"] / price24h - 1) * 100)
            else :
                data["baseVolume"]    = 0
                data["quoteVolume"]   = 0
                data["percentChange"] = 0
            r.update({market : data})
        return r

    def return24Volume(self):
        """ Returns the 24-hour volume for all markets, plus totals for primary currencies.

            Sample output:

            .. code-block:: json

                {
                    "USD_BTS": {
                        "BTS": 361666.63617,
                        "USD": 1087.0
                    },
                    "GOLD_BTS": {
                        "BTS": 0,
                        "GOLD": 0
                    }
                }

        """
        r = {}
        for market in self.markets :
            m = self.markets[market]
            marketHistory = self.ws.get_market_history(
                m["quote"], m["base"],
                24 * 60 * 60,
                self.formatTimeFromNow(-24 * 60 * 60),
                self.formatTimeFromNow(),
                api="history")
            quote_asset, base_asset = self.ws.get_objects([m["quote"], m["base"]])
            data = {}
            if len(marketHistory) :
                if marketHistory[0]["key"]["quote"] == m["quote"] :
                    data[m["base_symbol"]] = float(marketHistory[0]["base_volume"]) / (10 ** base_asset["precision"])
                    data[m["quote_symbol"]] = float(marketHistory[0]["quote_volume"]) / (10 ** quote_asset["precision"])
                else :
                    data[m["base_symbol"]] = float(marketHistory[0]["quote_volume"]) / (10 ** base_asset["precision"])
                    data[m["quote_symbol"]] = float(marketHistory[0]["base_volume"]) / (10 ** quote_asset["precision"])
            else :
                data[m["base_symbol"]] = 0
                data[m["quote_symbol"]] = 0
            r.update({market : data})
        return r

    def returnOrderBook(self, currencyPair="all", limit=25):
        """ Returns the order book for a given market. You may also
            specify "all" to get the orderbooks of all markets.

            :param str currencyPair: Return results for a particular market only (default: "all")
            :param int limit: Limit the amount of orders (default: 25)

            Ouput is formated as:::

                [price, amount]

            * price is denoted in base per quote
            * amount is in quote

            Sample output:

            .. code-block:: json

                {'USD_BTS': {'asks': [[0.0003787878787878788, 203.1935],
                [0.0003799587270281197, 123.65374999999999]], 'bids':
                [[0.0003676470588235294, 9.9], [0.00036231884057971015,
                10.0]]}, 'GOLD_BTS': {'asks': [[2.25e-05,
                0.045000000000000005], [2.3408239700374533e-05,
                0.33333333333333337]], 'bids': [[2.0833333333333333e-05,
                0.4], [1.851851851851852e-05, 0.0001]]}}

            .. note:: A maximum of 25 orders will be returned!

        """
        r = {}
        if currencyPair == "all" :
            markets = list(self.markets.keys())
        else:
            markets = [currencyPair]
        for market in markets :
            m = self.markets[market]
            orders = self.ws.get_limit_orders(
                m["quote"], m["base"], limit)
            quote_asset, base_asset = self.ws.get_objects([m["quote"], m["base"]])
            asks = []
            bids = []
            for o in orders:
                if o["sell_price"]["base"]["asset_id"] == m["base"] :
                    price = self._get_price(o["sell_price"])
                    volume = float(o["for_sale"]) / 10 ** base_asset["precision"] / self._get_price(o["sell_price"])
                    asks.append([price, volume])
                else :
                    price = 1 / self._get_price(o["sell_price"])
                    volume = float(o["for_sale"]) / 10 ** quote_asset["precision"]
                    bids.append([price, volume])

            data = {"asks" : asks, "bids" : bids}
            r.update({market : data})
        return r

    def returnBalances(self):
        """ Returns all of your balances.

            Example Output:

            .. code-block:: json

                {
                    "BROWNIE.PTS": 2499.9999,
                    "EUR": 0.0028,
                    "BTS": 1893552.94893,
                    "OPENBTC": 0.00110581,
                    "GREENPOINT": 0.0
                }

        """
        account = self.rpc.get_account(self.config.account)
        balances = self.ws.get_account_balances(account["id"], [])
        asset_ids = [a["asset_id"] for a in balances]
        assets = self.ws.get_objects(asset_ids)
        data = {}
        for i, asset in enumerate(assets) :
            amount = float(balances[i]["amount"]) / 10 ** asset["precision"]
            if amount == 0.0:
                continue
            data[asset["symbol"]] = amount
        return data

    def returnOpenOrdersIds(self, currencyPair="all"):
        """ Returns only the ids of open Orders
        """
        account = self.rpc.get_account(self.config.account)
        r = {}
        if currencyPair == "all" :
            markets = list(self.markets.keys())
        else:
            markets = [currencyPair]
        orders = self.ws.get_full_accounts([account["id"]], False)[0][1]["limit_orders"]
        for market in markets :
            r[market] = []
        for o in orders:
            quote_id = o["sell_price"]["quote"]["asset_id"]
            base_id = o["sell_price"]["base"]["asset_id"]
            quote_asset, base_asset = self.ws.get_objects([quote_id, base_id])
            for market in markets :
                m = self.markets[market]
                if ((o["sell_price"]["base"]["asset_id"] == m["base"] and
                    o["sell_price"]["quote"]["asset_id"] == m["quote"])
                    or (o["sell_price"]["base"]["asset_id"] == m["quote"] and
                        o["sell_price"]["quote"]["asset_id"] ==
                        m["base"])):
                    r[market].append(o["id"])
        return r

    def returnOpenOrders(self, currencyPair="all"):
        """ Returns your open orders for a given market, specified by
            the "currencyPair.

            :param str currencyPair: Return results for a particular market only (default: "all")

            Output Parameters:

                - `type`: sell or buy order for `quote`
                - `rate`: price for `base` per `quote`
                - `orderNumber`: identifier (e.g. for cancelation)
                - `amount`: amount of quote
                - `total`: amount of base at asked price (amount/price)
                - `amount_to_sell`: "amount_to_sell"

            .. note:: Ths method will not show orders of markets that
                      are **not** in the ``watch_markets`` array!

            Example:

            ::
                {
                    "USD_BTS": [
                        {
                            "orderNumber": "1.7.1505",
                            "type": "buy",
                            "rate": 341.74559999999997,
                            "total": 341.74559999999997,
                            "amount": 1.0
                        },
                        {
                            "orderNumber": "1.7.1512",
                            "type": "buy",
                            "rate": 325.904045,
                            "total": 325.904045,
                            "amount": 1.0
                        },
                        {
                            "orderNumber": "1.7.1513",
                            "type": "sell",
                            "rate": 319.45050000000003,
                            "total": 31945.05,
                            "amount": 1020486.2195025001
                        }
                    ]
                }

        """
        account = self.rpc.get_account(self.config.account)
        r = {}
        if currencyPair == "all" :
            markets = list(self.markets.keys())
        else:
            markets = [currencyPair]
        orders = self.ws.get_full_accounts([account["id"]], False)[0][1]["limit_orders"]
        for market in markets :
            r[market] = []
        for o in orders:
            quote_id = o["sell_price"]["quote"]["asset_id"]
            base_id = o["sell_price"]["base"]["asset_id"]
            quote_asset, base_asset = self.ws.get_objects([quote_id, base_id])
            for market in markets :
                m = self.markets[market]
                if (o["sell_price"]["base"]["asset_id"] == m["base"] and
                        o["sell_price"]["quote"]["asset_id"] == m["quote"]):
                    " selling "
                    amount = float(o["for_sale"]) / 10 ** quote_asset["precision"] * self._get_price(o["sell_price"])
                    rate = self._get_price(o["sell_price"])
                    t = "buy"
                    total = amount * rate
                    for_sale = float(o["for_sale"]) / 10 ** quote_asset["precision"]
                elif (o["sell_price"]["base"]["asset_id"] == m["quote"] and
                        o["sell_price"]["quote"]["asset_id"] == m["base"]):
                    " buying "
                    amount = float(o["for_sale"]) / 10 ** base_asset["precision"]
                    rate = 1 / self._get_price(o["sell_price"])
                    t = "sell"
                    total = amount * rate
                    for_sale = float(o["for_sale"]) / 10 ** base_asset["precision"]
                else :
                    continue
                r[market].append({"rate" : rate,
                                  "amount" : amount,
                                  "total" : total,
                                  "type" : t,
                                  "amount_to_sell" : for_sale,
                                  "orderNumber" : o["id"]})
        return r

    def returnTradeHistory(self, currencyPair="all", limit=25):
        """ Returns your trade history for a given market, specified by
            the "currencyPair" parameter. You may also specify "all" to
            get the orderbooks of all markets.

            :param str currencyPair: Return results for a particular market only (default: "all")
            :param int limit: Limit the amount of orders (default: 25)

            Output Parameters:

                - `type`: sell or buy
                - `rate`: price for `quote` denoted in `base` per `quote`
                - `amount`: amount of quote
                - `total`: amount of base at asked price (amount/price)

        """
        r = {}
        if currencyPair == "all" :
            markets = list(self.markets.keys())
        else:
            markets = [currencyPair]
        for market in markets :
            m = self.markets[market]
            filled = self.ws.get_fill_order_history(
                m["quote"], m["base"], 2 * limit, api="history")
            trades = []
            for f in filled[1::2] :  # every second entry "fills" the order
                data = {}
                data["date"] = f["time"]
                data["rate"] = self._get_price_filled(f, m)
                quote, base = self.ws.get_objects([m["quote"], m["base"]])
                if f["op"]["pays"]["asset_id"] == m["base"] :
                    data["type"]   = "buy"
                    data["amount"] = f["op"]["receives"]["amount"] / 10 ** quote["precision"]
                else :
                    data["type"]   = "sell"
                    data["amount"] = f["op"]["pays"]["amount"] / 10 ** quote["precision"]
                data["total"]  = data["amount"] * data["rate"]
                trades.append(data)

            r.update({market : trades})
        return r

    def buy(self, currencyPair, rate, amount):
        """ Places a buy order in a given market (buy ``quote``, sell
            ``base`` in market ``quote_base``). Required POST parameters
            are "currencyPair", "rate", and "amount". If successful, the
            method will return the order creating (signed) transaction.

            :param str currencyPair: Return results for a particular market only (default: "all")
            :param float price: price denoted in ``base``/``quote``
            :param number amount: Amount of ``quote`` to buy

            Prices/Rates are denoted in 'base', i.e. the USD_BTS market
            is priced in BTS per USD.

            **Example:** in the USD_BTS market, a price of 300 means
            a USD is worth 300 BTS

            .. note::

                All prices returned are in the **reveresed** orientation as the
                market. I.e. in the BTC/BTS market, prices are BTS per BTS.
                That way you can multiply prices with `1.05` to get a +5%.
        """
        if self.safe_mode :
            print("Safe Mode enabled!")
            print("Please GrapheneExchange(config, safe_mode=False) to remove this and execute the transaction below")
        # We buy quote and pay with base
        quote_symbol, base_symbol = currencyPair.split(self.market_separator)
        base = self.rpc.get_asset(base_symbol)
        quote = self.rpc.get_asset(quote_symbol)
        # Check amount > 0
        return self.rpc.sell_asset(self.config.account,
                                   '{:.{prec}f}'.format(amount * rate, prec=base["precision"]),
                                   base_symbol,
                                   '{:.{prec}f}'.format(amount, prec=quote["precision"]),
                                   quote_symbol,
                                   7 * 24 * 60 * 60,
                                   False,
                                   not self.safe_mode)

    def sell(self, currencyPair, rate, amount):
        """ Places a sell order in a given market (sell ``quote``, buy
            ``base`` in market ``quote_base``). Required POST parameters
            are "currencyPair", "rate", and "amount". If successful, the
            method will return the order creating (signed) transaction.

            :param str currencyPair: Return results for a particular market only (default: "all")
            :param float price: price denoted in ``base``/``quote``
            :param number amount: Amount of ``quote`` to sell

            Prices/Rates are denoted in 'base', i.e. the USD_BTS market
            is priced in BTS per USD.

            **Example:** in the USD_BTS market, a price of 300 means
            a USD is worth 300 BTS

            .. note::

                All prices returned are in the **reveresed** orientation as the
                market. I.e. in the BTC/BTS market, prices are BTS per BTS.
                That way you can multiply prices with `1.05` to get a +5%.
        """
        if self.safe_mode :
            print("Safe Mode enabled!")
            print("Please GrapheneExchange(config, safe_mode=False) to remove this and execute the transaction below")
        # We sell quote and pay with base
        quote_symbol, base_symbol = currencyPair.split(self.market_separator)
        base = self.rpc.get_asset(base_symbol)
        quote = self.rpc.get_asset(quote_symbol)
        return self.rpc.sell_asset(self.config.account,
                                   '{:.{prec}f}'.format(amount, prec=quote["precision"]),
                                   quote_symbol,
                                   '{:.{prec}f}'.format(amount * rate, prec=base["precision"]),
                                   base_symbol,
                                   7 * 24 * 60 * 60,
                                   False,
                                   not self.safe_mode)

    def close_debt_position(self, symbol):
        """ Close a debt position and reclaim the collateral

            :param str symbol: Symbol to close debt position for
            :raises ValueError: if symbol is not a bitasset
            :raises ValueError: if collateral ratio is smaller than maintenance collateral ratio
            :raises ValueError: if required amounts of collateral are not available
        """
        raise NotImplementedError  # TODO

    def adjust_debt(self, delta_debt, symbol, new_collateral_ratio=None):
        """ Adjust the amount of debt for an asset

            :param float delta_debt: Delta of the debt (-10 means reduce debt by 10, +10 means borrow another 10)
            :param str symbol: Asset to borrow
            :param float new_collateral_ratio: collateral ratio to maintain (optional, by default tries to maintain old ratio)
            :raises ValueError: if symbol is not a bitasset
            :raises ValueError: if collateral ratio is smaller than maintenance collateral ratio
            :raises ValueError: if required amounts of collateral are not available
        """
        raise NotImplementedError  # TODO

    def adjust_collateral_ratio(self, amount, symbol, target_collateral_ratio):
        """ Adjust the collataral ratio of a debt position

            :param float amount: Amount to borrow (denoted in 'asset')
            :param str symbol: Asset to borrow
            :param float target_collateral_ratio: desired collateral ratio
            :raises ValueError: if symbol is not a bitasset
            :raises ValueError: if collateral ratio is smaller than maintenance collateral ratio
            :raises ValueError: if required amounts of collateral are not available
        """
        raise NotImplementedError  # TODO

    def borrow(self, amount, symbol, collateral_ratio):
        """ Borrow bitassets/smartcoins from the network by putting up
            collateral in a CFD at a given collateral ratio.

            :param float amount: Amount to borrow (denoted in 'asset')
            :param str symbol: Asset to borrow
            :param float collateral_ratio: Collateral ratio to borrow at
            :raises ValueError: if symbol is not a bitasset
            :raises ValueError: if collateral ratio is smaller than maintenance collateral ratio
            :raises ValueError: if required amounts of collateral are not available

            Example Output:

            .. code-block:: json

                {
                    "ref_block_num": 14705,
                    "signatures": [],
                    "extensions": [],
                    "expiration": "2016-01-11T15:14:30",
                    "operations": [
                        [
                            3,
                            {
                                "funding_account": "1.2.282",
                                "delta_collateral": {
                                    "amount": 1080540000,
                                    "asset_id": "1.3.0"
                                },
                                "extensions": [],
                                "delta_debt": {
                                    "amount": 10000,
                                    "asset_id": "1.3.106"
                                },
                                "fee": {
                                    "amount": 100000,
                                    "asset_id": "1.3.0"
                                }
                            }
                        ]
                    ],
                    "ref_block_prefix": 1284843328
                }


        """
        if self.safe_mode :
            print("Safe Mode enabled!")
            print("Please GrapheneExchange(config, safe_mode=False) to remove this and execute the transaction below")
        # We sell quote and pay with base
        asset = self.rpc.get_asset(symbol)
        if "bitasset_data_id" not in asset:
            raise ValueError("%s is not a bitasset!" % symbol)
        bitasset = self.ws.get_objects([asset["bitasset_data_id"]])[0]

        # Check minimum collateral ratio
        backing_asset_id = bitasset["options"]["short_backing_asset"]
        maintenance_col_ratio = bitasset["current_feed"]["maintenance_collateral_ratio"] / 1000
        if maintenance_col_ratio > collateral_ratio:
            raise ValueError("Collateral Ratio has to be higher than %5.2f" % maintenance_col_ratio)

        # Derive Amount of Collateral
        collateral_asset = self.ws.get_objects([backing_asset_id])[0]
        settlement_price = self._get_price(bitasset["current_feed"]["settlement_price"])
        amount_of_collateral = amount * collateral_ratio / settlement_price

        # Verify that enough funds are available
        balances = self.returnBalances()
        fundsNeeded = amount_of_collateral + self.returnFees()["call_order_update"]["fee"]
        fundsHave = balances[collateral_asset["symbol"]]
        if fundsHave <= fundsNeeded:
            raise ValueError("Not enough funds available. Need %f %s, but only %f %s are available" %
                             (fundsNeeded, collateral_asset["symbol"], fundsHave, collateral_asset["symbol"]))

        # Borrow
        return self.rpc.borrow_asset(self.config.account,
                                     '{:.{prec}f}'.format(amount, prec=asset["precision"]),
                                     symbol,
                                     '{:.{prec}f}'.format(amount_of_collateral, prec=collateral_asset["precision"]),
                                     not self.safe_mode)

    def cancel(self, orderNumber):
        """ Cancels an order you have placed in a given market. Requires
            only the "orderNumber". An order number takes the form
            ``1.7.xxx``.

            :param str orderNumber: The Order Object ide of the form ``1.7.xxxx``
        """
        if self.safe_mode :
            print("Safe Mode enabled!")
            print("Please GrapheneExchange(config, safe_mode=False) to remove this and execute the transaction below")
        # return self.rpc.cancel_order(orderNumber, not self.safe_mode)

        account = self.rpc.get_account(self.config.account)
        op          = self.rpc.get_prototype_operation("limit_order_cancel_operation")
        op[1]["fee_paying_account"] = account["id"]
        op[1]["order"] = orderNumber
        buildHandle = self.rpc.begin_builder_transaction()
        self.rpc.add_operation_to_builder_transaction(buildHandle, op)
        self.rpc.set_fees_on_builder_transaction(buildHandle, "1.3.0")
        return self.rpc.sign_builder_transaction(buildHandle, True)

    def withdraw(self, currency, amount, address):
        """ This Method makes no sense in a decentralized exchange
        """
        raise NotImplementedError
