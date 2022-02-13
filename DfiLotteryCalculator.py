import ccxt, datetime, requests
from argparse import RawDescriptionHelpFormatter
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.parser import parse
from cryptography.hazmat.primitives import hashes

class DfiLotteryCalculator:

    def __init__(self, logger, subparsers):
        self.__logger = logger
        self.__build_menu(subparsers)

    def __build_menu(self, subparsers):
        desc = "Executes the DFI Community Lottery calculations\n\nExample run:\npython3 ./dfi_lotto_calc.py -c dfi_lotto_calc.conf calc -t 60 -d 2022-02-05 -b 1598835 -dfi 2.793 -btc 41603.4\n\n####### Things to note: #######\n"+ \
        "\t1. -b/-block_id argument must be a DFI blockchain block from the target date.  dfi_lotto_calc will attempt to find the first block from that day using https://defiscan.live/ , so the blockID can be given or the block hash.  This is done through a recursive function, which may fail if a beginning search block close enough to midnight is NOT picked.\n" + \
        "\t2. If -D/-debug option is given the KuCoin sandbox mode will be used.  The sandbox does NOT have a DFI/USDT price, so ETH/USDT is used in it's place.  KuCoin's price history is not very extensive, so if the lookup fails the -dfi/-btc arguments MUST be provided.  If dfi_lotto_calc is run close enough to midnight the day of -d/target_date the KuCoin lookup should work!\n" + \
            "###############################"
        sub_parser = subparsers.add_parser("calc", description=desc,
                                           formatter_class=RawDescriptionHelpFormatter)
        sub_parser.add_argument("-v", "-verbose", dest="verbose", action='store_true', required=False,
                                help="Set verbose option for more output/logging")
        sub_parser.add_argument("-t", "-total_tickets", dest="total_tickets", default=None, required=True,
                                help="Total # of lottery tickets for this drawing")
        sub_parser.add_argument("-d", "-target_date", dest="target_date", default=None, required=True,
                                help="Date for this drawing (ex: 2022-02-05)")
        sub_parser.add_argument("-b", "-block_id_from_date", dest="block_id_from_date", default=None, required=True,
                                help="Block ID or Block Hash from target_date")
        sub_parser.add_argument("-dfi", "-dfi_price", dest="dfi_price", default=None, required=False,
                                help="DFI/USDT price at midnight of target date on KuCoin")
        sub_parser.add_argument("-btc", "-btc_price", dest="btc_price", default=None, required=False,
                                help="BTC/USDT price at midnight of target date on KuCoin")
        sub_parser.add_argument("-ak", "-api_key", dest="api_key", default=None, required=False,
                                help="KuCoin API Key")
        sub_parser.add_argument("-as", "-api_secret", dest="api_secret", default=None, required=False,
                                help="KuCoin API Secret")
        sub_parser.add_argument("-ap", "-api_password", dest="api_password", default=None, required=False,
                                help="KuCoin API Password")
        sub_parser.add_argument("-D", "-debug", dest="DEBUG", action='store_true', required=False,
                                help="Debug mode (NOTE: This will set KuCoin to sandbox mode and use ETH/USDT instead of DFI/USDT for price metrics)")
        sub_parser.add_argument("-o", dest="outDir", default=".", help="Directory to write output files (default: .)")
        sub_parser.set_defaults(func=self.__main)

    def __main(self, args):
        global DEBUG, verbose, defiscan_block_url, block_hash, timestamp, minter, next_block, prev_block
        DEBUG=args.DEBUG
        verbose=args.verbose

        defiscan_block_url = 'https://defiscan.live/blocks/'
        btc_symbol = 'BTC/USDT'
        if (DEBUG):
            dfi_symbol = 'ETH/USDT'
        else:
            dfi_symbol = 'DFI/USDT'

        #print(ccxt.exchanges) # print a list of all available exchange classes

        dfi_block_from_target_date = args.block_id_from_date
        target_date_string = args.target_date
        total_number_of_tickets = int(args.total_tickets)
        if (verbose):
            print("Init args:\n\tdfi_block_from_target_date:",dfi_block_from_target_date,"\n\ttarget_date_string:",target_date_string,"\n\ttotal_number_of_tickets:",total_number_of_tickets)
        api_key = args.api_key
        api_secret = args.api_secret
        api_password = args.api_password
        if (args.verbose):
            print("KuCoin API args:\n\tapi_key:",api_key,"\n\tapi_secret:",api_secret,"\n\tapi_password:",api_password)

        if (api_key is None or api_secret is None or api_password is None):
            print("ERROR: KuCoin API details are NOT set!  Exiting!")
            exit(1)

        kucoin = ccxt.kucoin({
            'apiKey': api_key,
            'secret': api_secret,
            "password": api_password
        })
        if (DEBUG):
            print("DEBUG mode detected, setting Kucoin sandbox mode to TRUE")
            kucoin.set_sandbox_mode(True)

        # sample Kucoin request
        print("Testing KuCoin connection...")
        response = kucoin.fetch_ticker(btc_symbol)
        if (not response or response is None):
            print("FAILED!  Please verify your KuCoin API details (Hint: add verbose argument to print them to screen)")
        else:
            print("SUCCESS!")
            if (verbose):
                print(response)

        target_date = parse(target_date_string)
        current_time = datetime.now()
        if (target_date.year != current_time.year or target_date.month != current_time.month or target_date.day != current_time.day):
            print("WARNING: target_date(",target_date,") is not today: ", current_time,"")
            print("WARNING: KuCoin price history is NOT extensive, checking arguments for BTC and DFI price on target date...")
            try:
                if (args.btc_price is None or args.dfi_price is None):
                    print("arguments btc_price and dfi_price MUST be set to continue!  Exiting!")
                    exit(1)
                else:
                    dfi_at_midnight = float(args.dfi_price)
                    btc_at_midnight = float(args.btc_price)
            except:
                print("arguments btc_price and dfi_price MUST be set to continue!  Exiting!")
                exit(1)
        else:
            print("############# Fetching ",dfi_symbol," & ",btc_symbol," prices at midnight of target_date (",target_date,") from KuCoin #############")
            btc_at_midnight = self.fetch_midnight_price_at_close(kucoin, btc_symbol, target_date)
            dfi_at_midnight = self.fetch_midnight_price_at_close(kucoin, dfi_symbol, target_date)

        print("dfi_at_midnight: ", dfi_at_midnight)
        print("btc_at_midnight: ", btc_at_midnight)
        if (not btc_at_midnight or btc_at_midnight is None or not dfi_at_midnight or dfi_at_midnight is None):
            if (DEBUG):
                if (dfi_at_midnight is None or not dfi_at_midnight):
                    print("WARNING!  Could not determine proper dfi_at_midnight, using 1.0")
                    dfi_at_midnight = 1.0
                if (btc_at_midnight is None or not btc_at_midnight):
                    print("WARNING!  Could not determine proper btc_at_midnight, using 1.0")
                    btc_at_midnight = 1.0
            else:
                print("ERROR: Could not determine prices for ",dfi_symbol," and/or ",btc_symbol, "!  Exiting!")
                exit(1)

        multiply_dfi_by_btc = round(btc_at_midnight * dfi_at_midnight)

        print("multiply_dfi_by_btc: ", multiply_dfi_by_btc)

        # TODO: narrow in
        print("############# Determing first DFI chain block of target_date (",target_date,"), starting from block #",dfi_block_from_target_date," #############")
        print("Please be patient, this could take awhile...")
        first_block_of_target_date = self.narrow_in_on_first_block(dfi_block_from_target_date, target_date)
        if (first_block_of_target_date == 0):
            print("ERROR: Could not determine first_block_of_target_date!  Exiting!")
            exit(1)
        self.get_block_hash_timestamp_minter(first_block_of_target_date)

        last_4_digits_of_block_hash = block_hash[len(block_hash)-4:len(block_hash)]
        print("last_4_digits_of_block_hash: ", last_4_digits_of_block_hash)

        last_4_digits_of_block_minter = minter[len(minter)-4:len(minter)]
        print("last_4_digits_of_block_minter: ", last_4_digits_of_block_minter)

        first_concat = "{}{}{}{}".format(multiply_dfi_by_btc,first_block_of_target_date,last_4_digits_of_block_hash,last_4_digits_of_block_minter)
        print("first_concat: ", first_concat)

        digest = hashes.Hash(hashes.SHA256())
        digest.update(bytes(first_concat, 'utf-8'))
        sha256_result = digest.finalize().hex()
        print("sha256_result: ", sha256_result)

        first5_of_hash = sha256_result[0:5]
        last5_of_hash = sha256_result[len(sha256_result)-5:len(sha256_result)]
        second_concat = "{}{}".format(first5_of_hash,last5_of_hash)
        print("second_concat: ", second_concat)

        # conversion to decimal
        decimal_of_second_concat = int(second_concat, 16)
        print("decimal_of_second_concat: ", decimal_of_second_concat)
        decimal_result = decimal_of_second_concat / pow(16, 10)
        print("decimal_result: ", decimal_result)
        print("total_number_of_tickets: ", total_number_of_tickets)
        winning_ticket = round(decimal_result * total_number_of_tickets)
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!!!!!!!! winning_ticket: ", winning_ticket," !!!!!!!!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

        print("############# CSV Output for Google Doc #############")
        csv_header_string = "KuCoin USDT Price of DFI,KuCoin USDT Price of BTC,Result of Multiplication of Price of DFI and Price of BTC,First Block After ",target_date_string,",Last 4 digits of Block Hash,Last 4 digits of Block Minter,1st Concatenation,SHA-256 Hash,2nd Concatenation,Decimal,Number,Winning Ticket,Jackpot (DFI),Burned (DFI)"
        print(csv_header_string)
        self.__logger.info(csv_header_string)
        csv_logger_string = dfi_at_midnight,",",btc_at_midnight,",",multiply_dfi_by_btc,",",first_block_of_target_date,",",last_4_digits_of_block_hash,",",last_4_digits_of_block_minter,",",first_concat,",",sha256_result,",",second_concat,",",decimal_result,",",winning_ticket,""
        print(csv_logger_string)
        self.__logger.info(csv_logger_string)

    def fetch_midnight_price_at_close(self, kucoin, symbol, target_date):
        #print(kucoin.fetch_ticker(symbol))
        price_at_close = ''
        timeframe = '5m'
        since = None
        '''
        if (DEBUG):
            since = None
        else:
            since = int(round(target_date.timestamp()))
            print("Setting KuCoin since date to: ",target_date,"(",since,")")
        '''
        limit = 1000
        ohlcvs = kucoin.fetch_ohlcv(symbol, timeframe, since, limit)
        #print(ohlcvs)

        beginning_of_target_date = datetime(target_date.year, target_date.month, target_date.day)
        #print("beginning_of_target_date: ", beginning_of_target_date)
        for candle in ohlcvs:
            if (verbose):
                print(candle)
            # candle[0] = Start time of the candle cycle
            # candle[1] = open
            # candle[2] = close
            # candle[3] = high
            # candle[4] = low
            # candle[5] = volume
            # candle[6] = turnover

            dt_object = datetime.fromisoformat(kucoin.iso8601(candle[0]).replace("Z", ""))
            if (dt_object == beginning_of_target_date):
                price_at_close = candle[2]
                #print('from', dt_object,candle[1], "price_at_close:", price_at_close)
        if (DEBUG):
            print("price at midnight: ", price_at_close)
        return price_at_close

    def narrow_in_on_first_block(self, block_from_date, target_date):
        global block_hash, timestamp, minter, next_block, prev_block

        # first, let's check that block_from_date matches our target_date
        self.get_block_hash_timestamp_minter(block_from_date)
        timestamp_date = parse(timestamp)
        #print("target_date: ", target_date)
        #print("timestamp_date: ", timestamp_date)
        if (target_date.year != timestamp_date.year or target_date.month != timestamp_date.month or target_date.day != timestamp_date.day):
            print("Error: block_from_date(",block_from_date,") is not from target_date: ", target_date)
            return 0
        first_block_of_target_date = self.find_first_block_of_date(block_from_date, target_date)
        return first_block_of_target_date

    def find_first_block_of_date(self, block, target_date):
        self.get_block_hash_timestamp_minter(block)
        print("#### Examining block #",block,":",timestamp)
        timestamp_date = parse(timestamp)
        if ((target_date.day - 1) == timestamp_date.day):
            print("first_block_of_target_day: ", next_block)
            return next_block
        else:
            return self.find_first_block_of_date(prev_block, target_date)

    def get_block_hash_timestamp_minter(self, block):
        global block_hash, timestamp, minter, next_block, prev_block
        # the target we want to open
        url=defiscan_block_url+str(block)

        #open with GET method
        #print("#### ", block, " #### : Fetching DFI block info from URL: ", url)
        resp=requests.get(url)

        #http_respone 200 means OK status
        if resp.status_code==200:
            #print("Successfully opened the web page")

            # we need a parser, Python built-in HTML parser is enough .
            soup=BeautifulSoup(resp.text,'html.parser')

            # block_hash_search is the list which contains all the text in the tag we are searching for
            block_hash_search=soup.find("div",{"class":"ml-1 text-lg break-all"})
            #print(block_hash_search)
            block_hash = self.parse_value_from_div(block_hash_search)
            if (verbose):
                print("#### ", block, " #### : block_hash : ", block_hash)

            timestamp_field_search=soup.findAll("div",{"class":"table-cell px-4 md:px-6 py-3 text-gray-600 align-middle"})
            #print(timestamp_field_search)
            timestamp = self.parse_value_from_div(timestamp_field_search[2])
            if (verbose):
                print("#### ", block, " #### : timestamp  : ", timestamp)

            prev_block = self.parse_value_from_div_with_url2(timestamp_field_search[len(timestamp_field_search)-2])
            if (verbose):
                print("#### ", block, " #### : prev_block : ", prev_block)

            next_block = self.parse_value_from_div_with_url2(timestamp_field_search[len(timestamp_field_search)-1])
            if (verbose):
                print("#### ", block, " #### : next_block : ", next_block)

            minter_search=soup.find("div",{"class":"hover:underline text-blue-500 cursor-pointer break-all"})
            #print(minter_search)
            minter = self.parse_value_from_div_with_url(minter_search)
            if (verbose):
                print("#### ", block, " #### : minter     : ", minter)

            return block_hash
        else:
            print("ERROR fetching DFI block info from URL: ", url)

    def parse_value_from_div(self, html):
        splitter1 = str(html).split(">")
        #print(splitter1)
        splitter2 = splitter1[1].split("<")
        #print(splitter2)
        value = splitter2[0]
        return value

    def parse_value_from_div_with_url(self, html):
        splitter1 = str(html).split(">")
        #print(splitter1)
        splitter2 = splitter1[2].split("<")
        #print(splitter2)
        value = splitter2[0]
        return value

    def parse_value_from_div_with_url2(self, html):
        splitter1 = str(html).split(">")
        #print(splitter1)
        splitter2 = splitter1[3].split("<")
        #print(splitter2)
        splitter3 = splitter2[0].split("#")
        #print(splitter3)
        value = splitter3[1]
        return value