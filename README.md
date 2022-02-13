# dfi_community_lotto
Utility to help do the necessary calculations for the DFI Community Lottery

## Lottery Info:
https://sites.google.com/view/defichaincommunitylotto/home?authuser=0

## Built-in help:
```
> python3 ./dfi_lotto_calc.py calc -h
usage: dfi_lotto_calc calc [-h] [-v] -t TOTAL_TICKETS -d TARGET_DATE -b
                           BLOCK_ID_FROM_DATE [-dfi DFI_PRICE]
                           [-btc BTC_PRICE] [-ak API_KEY] [-as API_SECRET]
                           [-ap API_PASSWORD] [-D] [-o OUTDIR]

Executes the DFI Community Lottery calculations

optional arguments:
  -h, --help            show this help message and exit
  -v, -verbose          Set verbose option for more output/logging
  -t TOTAL_TICKETS, -total_tickets TOTAL_TICKETS
                        Total # of lottery tickets for this drawing
  -d TARGET_DATE, -target_date TARGET_DATE
                        Date for this drawing (ex: 2022-02-05)
  -b BLOCK_ID_FROM_DATE, -block_id_from_date BLOCK_ID_FROM_DATE
                        Block ID from target_date
  -dfi DFI_PRICE, -dfi_price DFI_PRICE
                        DFI/USDT price at midnight of target date on KuCoin
  -btc BTC_PRICE, -btc_price BTC_PRICE
                        BTC/USDT price at midnight of target date on KuCoin
  -ak API_KEY, -api_key API_KEY
                        KuCoin API Key
  -as API_SECRET, -api_secret API_SECRET
                        KuCoin API Secret
  -ap API_PASSWORD, -api_password API_PASSWORD
                        KuCoin API Password
  -D, -debug            Debug mode (NOTE: This will set KuCoin to sandbox mode
                        and use ETH/USDT instead of DFI/USDT for price
                        metrics)
  -o OUTDIR             Directory to write output files (default: .)
```
## DEBUG option (-D) to use KuCoin sandbox mode!
```
> python3 ./dfi_lotto_calc.py -c dfi_lotto_calc.conf calc -D -t 60 -d 2022-02-05 -b 1598835 -dfi 2.793 -btc 41603.4
DEBUG mode detected, setting Kucoin sandbox mode to TRUE
Testing KuCoin connection...
SUCCESS!
WARNING: target_date( 2022-02-05 00:00:00 ) is not today:  2022-02-13 10:33:50.257407
WARNING: KuCoin price history is NOT extensive, checking arguments for BTC and DFI price on target date...
dfi_at_midnight:  2.793
btc_at_midnight:  41603.4
multiply_dfi_by_btc:  116198
############# Determing first DFI chain block of target_date ( 2022-02-05 00:00:00 ), starting from block # 1598835  #############
Please be patient, this could take awhile...
#### Examining block # 1598835 : Feb 5, 2022, 12:00:02 AM
#### Examining block # 8758f7957341b17f781af71f4a4e8b2a932dfcaddf9fad8fcc5e4d7fa4298823 : Feb 4, 2022, 11:59:13 PM
first_block_of_target_day:  1598835
last_4_digits_of_block_hash:  e4a9
last_4_digits_of_block_minter:  k1cn
first_concat:  1161981598835e4a9k1cn
sha256_result:  28505e2b32e56684c96fc85273b793ac60f808294c25f2b72bdb838f79a6cd11
second_concat:  285056cd11
decimal_of_second_concat:  173146557713
decimal_result:  0.15747587687019404
total_number_of_tickets:  60

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!! winning_ticket:  9  !!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

############# CSV Output for Google Doc #############
KuCoin USDT Price of DFI,KuCoin USDT Price of BTC,Result of Multiplication of Price of DFI and Price of BTC,First Block After  2022-02-05 ,Last 4 digits of Block Hash,Last 4 digits of Block Minter,1st Concatenation,SHA-256 Hash,2nd Concatenation,Decimal,Number,Winning Ticket,Jackpot (DFI),Burned (DFI)
2.793 , 41603.4 , 116198 , 1598835 , e4a9 , k1cn , 1161981598835e4a9k1cn , 28505e2b32e56684c96fc85273b793ac60f808294c25f2b72bdb838f79a6cd11 , 285056cd11 , 0.15747587687019404 , 9
```

## Example Run:
```
> python3 ./dfi_lotto_calc.py -c dfi_lotto_calc.conf calc -t 60 -d 2022-02-13 -b 1621702
Testing KuCoin connection...
SUCCESS!
############# Fetching  DFI/USDT  &  BTC/USDT  prices at midnight of target_date ( 2022-02-13 00:00:00 ) from KuCoin #############
dfi_at_midnight:  3.53
btc_at_midnight:  42222.4
multiply_dfi_by_btc:  149045
############# Determing first DFI chain block of target_date ( 2022-02-13 00:00:00 ), starting from block # 1621702  #############
Please be patient, this could take awhile...
#### Examining block # 1621702 : Feb 13, 2022, 12:00:49 AM
#### Examining block # 3a48d9f20f748a8765381c0e2007f140fcffb26a2e3707ec391985a9378af5b5 : Feb 13, 2022, 12:00:23 AM
#### Examining block # e66797f804cc784148e6ea63ec016bcf5284fc34966f2c8072176842ba6d441c : Feb 12, 2022, 11:59:33 PM
first_block_of_target_day:  1621701
last_4_digits_of_block_hash:  f5b5
last_4_digits_of_block_minter:  XYF1
first_concat:  1490451621701f5b5XYF1
sha256_result:  332790d79ac7f1ce05013356d3289a2e7e1419667c7b268b50075dfdd3ba8870
second_concat:  33279a8870
decimal_of_second_concat:  219707770992
decimal_result:  0.19982305365556385
total_number_of_tickets:  60

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!! winning_ticket:  12  !!!!!!!!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

############# CSV Output for Google Doc #############
KuCoin USDT Price of DFI,KuCoin USDT Price of BTC,Result of Multiplication of Price of DFI and Price of BTC,First Block After  2022-02-13 ,Last 4 digits of Block Hash,Last 4 digits of Block Minter,1st Concatenation,SHA-256 Hash,2nd Concatenation,Decimal,Number,Winning Ticket,Jackpot (DFI),Burned (DFI)
3.53 , 42222.4 , 149045 , 1621701 , f5b5 , XYF1 , 1490451621701f5b5XYF1 , 332790d79ac7f1ce05013356d3289a2e7e1419667c7b268b50075dfdd3ba8870 , 33279a8870 , 0.19982305365556385 , 12
```
