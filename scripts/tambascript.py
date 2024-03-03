from hummingbot.strategy.script_strategy_base import ScriptStrategyBase
from hummingbot.connector.connector_base import ConnectorBase
from hummingbot.core.data_type.common import OrderType
from hummingbot.strategy.strategy_py_base import (
    BuyOrderCompletedEvent,
    BuyOrderCreatedEvent,
    OrderFilledEvent,
    SellOrderCompletedEvent,
    SellOrderCreatedEvent,
    MarketOrderFailureEvent,
)
from decimal import *
import time
import logging
class TambaScript(ScriptStrategyBase):
    #NE VALTOZTASD CSAK HA MASIK BASE KRIPTOT AKARSZ HASZNALNI
    base = "USDT"
    #VALTOZTASD ARRA AMELYIK KRIPTOT AKAROD TRADELNI
    crypto = "AI"
    #HA NEM TESTNET AKKOR IRD AT exchange = "binance" RE
    exchange = "binancetestnet"

    markets = {exchange: {f"{crypto}-{base}"}}
    
    
    boughtCrypto = False
    soldCrypto = False
    filledBuy = False
    filledSell = False
    #IRD AT A ZAROJELBE LEVO ERTEKET ARRA HOGY HANY SZAZALEKOS THRESHOLDDAL MUKODJON
    threshold = Decimal(0.02)
    peakPrice = 0
    basePrice = 0
    sellPrice = 0
    #CSAK A 99%AT HASZNALJA A BALANCENAK HOGY MINDIG LEGYEN PUFFER MERT NEHA BUGOL, DE HA KISERLETEZNI AKARSZ CSAPD FEL 100RA
    percentageOfBalance = 99
    buyinit = True
    sellinit = True
    boughtAmount = 0
    balance = 0
    

    def on_tick(self):
        if self.buyinit:
            self.boughtAmount = 0
            currentPrice = self.connectors[self.exchange].get_mid_price(f"{self.crypto}-{self.base}")
            self.balance = self.connectors[self.exchange].get_balance(self.base) * Decimal((self.percentageOfBalance/100))
            msg = f"Starting balance:{self.balance}"
            self.logger().info(msg)
            self.notify_hb_app_with_timestamp(msg)
            self.peakPrice = currentPrice
            self.basePrice = currentPrice
            if not currentPrice.is_nan():
                self.buyinit = False
        
        if not self.filledBuy:
            currentPrice = self.connectors[self.exchange].get_mid_price(f"{self.crypto}-{self.base}")
            msg = f"BUY PHASE --  Current price:{currentPrice} BuyPrice:{self.basePrice + (self.basePrice * self.threshold / 100)}"
            self.logger().info(msg)
            if currentPrice > self.peakPrice:
                self.peakPrice = currentPrice
            if currentPrice < self.basePrice:
                self.basePrice = currentPrice
                self.peakPrice = currentPrice
            if self.peakPrice >= self.basePrice + (self.basePrice * self.threshold / 100):
                msg = f"Buying crypto at this price -> {currentPrice}"
                amount = self.connectors[self.exchange].get_balance(self.base) * Decimal((self.percentageOfBalance/100)) / currentPrice
                self.logger().info(msg)
                self.notify_hb_app_with_timestamp(msg)
                self.buy(
                    connector_name=self.exchange,
                    trading_pair=f"{self.crypto}-{self.base}",
                    amount=Decimal(amount),
                    order_type=OrderType.MARKET,
                    price=Decimal(currentPrice)
                )
                self.boughtCrypto = True
                
        if self.filledBuy and not self.filledSell:
            if self.sellinit:
                msg = f"Entering selling phase!"
                self.logger().info(msg)
                self.notify_hb_app_with_timestamp(msg)
                currentPrice = self.connectors[self.exchange].get_mid_price(f"{self.crypto}-{self.base}")
                self.basePrice = currentPrice
                self.sellPrice = self.basePrice - (self.basePrice * self.threshold / 100)
                if not currentPrice.is_nan():
                    self.sellinit = False
            currentPrice = self.connectors[self.exchange].get_mid_price(f"{self.crypto}-{self.base}")
            assetBalance = self.connectors[self.exchange].get_balance(self.crypto)
            if assetBalance != self.boughtAmount:
                self.boughtAmount = assetBalance
            msg = f"SELL PHASE --  Current price:{currentPrice} SellPrice:{self.sellPrice}"
            self.logger().info(msg)
            if currentPrice > self.basePrice:
                self.basePrice = currentPrice
                self.sellPrice = self.basePrice - (self.basePrice * self.threshold / 100)
            if currentPrice <= self.sellPrice:
                msg = f"Selling crypto at this price -> {currentPrice}"
                self.logger().info(msg)
... (64 lines left)
Collapse
message.txt
8 KB
es escape utana kettospont es wq
es utana mehetsz vissza hummingbotba screen -r bot commanddal es indithatod ujra
ja persze mielott wqzol ird at a szazalekot meg testnetet torold ki az exchangebol
NBalazs — 02/22/2024 8:39 AM
Image
Na most mibaja?
Az egész helyére kellett bemásolni ugye?
Hiába írom be hogy stop, végig azt írja, hogy fut amikor el akarom indítani
bnc — 02/22/2024 8:50 AM
egesz helyere aha
hat azt tudod hogy exitet beirod
es utana ujra ./start
NBalazs — 02/22/2024 8:53 AM
Image
Ugyanaz
bnc — 02/22/2024 8:54 AM
el lett irva valami akkor
a tambascript.py-ba
NBalazs — 02/22/2024 8:58 AM
Megy
bnc — 02/22/2024 8:59 AM
na fasza
elvileg most mar ezt a fee-s issuet megkeruli
megnezi hogy a bevasarolt mennyiseg meg a binance fiokon levo mennyiseg kulonbozik-e es ha igen akkor a binanceos amountot hasznalja
NBalazs — 02/22/2024 8:59 AM
Viszont nem tudok ki ctrl a faszomolni
bnc — 02/22/2024 9:00 AM
akkor stoppold le, exit, irj be hogy screen -S nev es utana abbol inditsd
es akkor mar kienged lepni
sikerult?
NBalazs — 02/22/2024 9:06 AM
Nem xd
bnc — 02/22/2024 9:06 AM
damn
NBalazs — 02/22/2024 9:09 AM
Image
bnc — 02/22/2024 9:09 AM
fut a bot a hatterbe?
gondolom masik screenen van
screen -ls
es kiirja hogy milyen screenek futnak
ja hulye vagyok
NBalazs — 02/22/2024 9:10 AM
Image
Pfu
bnc — 02/22/2024 9:10 AM
vagy netom
XDDD
arra amelyik attached ugy tudsz ramenni hogy screen -r -d NEV
amelyik detached arra meg ugy hogy screen -r NEV
es ha ramesz egyre ha az nem az ami kellene akkor nyomj egy screen -X -S NEV kill commandot
es akkor eltunik
bnc — 02/22/2024 9:23 AM
sikerult?
NBalazs — 02/22/2024 10:35 AM
Tárgyaláson vagyok, majd délután próbálkozok
NBalazs — 02/22/2024 11:34 AM
Image
Na most mit basztam el? xd
Kinyírtam az összes screent
bnc — 02/22/2024 11:34 AM
cd hummingbot
nem jo mappaba vagy
NBalazs — 02/22/2024 11:35 AM
Ja tényleg
Jó na most elindult, akkor stopoljam le, exiteljek es screen -S név?
bnc — 02/22/2024 11:37 AM
aha
NBalazs — 02/22/2024 11:43 AM
Beírom hogy screen -S 22799.bot
Azt semmi
Image
Így kidob
bnc — 02/22/2024 11:43 AM
a screen -S letrehoz egyet
screen -r kell
NBalazs — 02/22/2024 11:44 AM
JA geci
bnc — 02/22/2024 11:44 AM
most gondolom megint csinaltal egy parat XDD
NBalazs — 02/22/2024 11:45 AM
Image
De arra meg azt írja, hogy nincs ilyen
Azt közben ott van
bnc — 02/22/2024 11:46 AM
screen -ls mit hoz?
NBalazs — 02/22/2024 11:46 AM
Image
bnc — 02/22/2024 11:47 AM
screen -D 22799.bot
ezt ird be
es utana screen -r
NBalazs — 02/22/2024 11:48 AM
[remote power detached from 22799.bot]
Connection to 141.147.14.221 closed.
Ledobott az egészről xd
bnc — 02/22/2024 11:49 AM
mi xd
XDD
wtf
sshzz vissza
es megint irj egy screen -lst
NBalazs — 02/22/2024 11:52 AM
(base) ubuntu@bot:~$ screen -ls
There are screens on:
    22799.bot    (02/22/24 10:37:58)    (Detached)
    5614.pts-0.bot    (02/21/24 20:46:50)    (Detached)
2 Sockets in /run/screen/S-ubuntu.
bnc — 02/22/2024 11:54 AM
megprobalhatsz a  22799.bot-re felmenni
ha az nem jo
akkor screen -r 5614.pts-0.bot
nemtom miert lett ketto
NBalazs — 02/22/2024 11:57 AM
Image
Így szétesik az egész ha megrpóbálom
Azt a gitclonet a görgetés miatt írta be
De le is fagy
bnc — 02/22/2024 11:57 AM
wtf
de most akkor neked van egy screened ahol elinditottad a botot es ctrl+a d-vel kijottel belole?
NBalazs — 02/22/2024 11:58 AM
Sima exit-el jöttem ki
mert a ctrl a d nem működik 
bnc — 02/22/2024 11:58 AM
ja de akkor igazabol tokmind1 h vannak ezek a screenek
annyi akkor hogy keszits egy uj screent
NBalazs — 02/22/2024 12:06 PM
./start-ra beenged simán
Meg el is tudom indítani a botot
Azzal nincs baj
bnc — 02/22/2024 12:07 PM
es nem tudsz kijonni belole ctrl+a d-vel?
NBalazs — 02/22/2024 12:07 PM
NEm
Image
Megyen szépen pedig
bnc — 02/22/2024 12:09 PM
ctrl A meg ctrl D?
az nem mukodik?
NBalazs — 02/22/2024 12:34 PM
Nem
bnc — 02/22/2024 12:34 PM
hat nem ertem geci
hat jobb otletem nincs max azt leeht hogy atdobod az ssh keyt aztan felmegyek megnezem nekem mukodik-e
mert nalam mukodik az en oracles hostomon
NBalazs — 02/22/2024 12:40 PM
Hogy a faszomba bírsz programozó lenni, hát már most agyvérzést kapok xddd
bnc — 02/22/2024 12:40 PM
xddddddddddd
15 eve ezt csinalom, jol birom a gyurodest
NBalazs — 02/22/2024 12:43 PM
Megyek vissza tárgyalásra majd utána matekozunk tovább
bnc — 02/22/2024 12:43 PM
jojo
NBalazs — 02/22/2024 12:51 PM
Nem értem
Még egy utolsót próbálkoztam
És most működött xd
bnc — 02/22/2024 12:51 PM
xddddddddddddddd
nemtudom en se hogy mi lehet
lehet a maces keyboarddal van valami bugja
NBalazs — 02/22/2024 12:52 PM
Akkor innentől screen -r 22799.bot
Így tudok visszamenni igaz?
bnc — 02/22/2024 12:52 PM
hat talan?
nemtom
xddd
screen -ls
NBalazs — 02/22/2024 12:52 PM
xddd
There are screens on:
    22799.bot    (02/22/24 10:37:58)    (Detached)
    5614.pts-0.bot    (02/21/24 20:46:50)    (Attached)
bnc — 02/22/2024 12:53 PM
akkor igen
NBalazs — 02/22/2024 12:53 PM
Arról szedett most le
bnc — 02/22/2024 12:53 PM
de probald meg
NBalazs — 02/22/2024 12:53 PM
Visszadobott és fut
bnc — 02/22/2024 12:53 PM
cool
perfect
NBalazs — 02/22/2024 12:53 PM
Na bezárom a terminalt és kipróbálom úgy is
bnc — 02/22/2024 12:53 PM
ja csak elotte menj ki
ctrla + dvel
xddd
NBalazs — 02/22/2024 12:54 PM
Működik
bnc — 02/22/2024 12:54 PM
parade
NBalazs — 02/22/2024 12:54 PM
Jó ez a programozás, magától megoldódnak dolgok
NBalazs — 02/22/2024 3:34 PM
Megcsinálta a vételt, de telegrácson nem jelezte
bnc — 02/22/2024 3:34 PM
wtf
NBalazs — 02/22/2024 3:39 PM
Nem vágom mert a bottal kommunikál
Ha megnyomok valamit telegramon, írja a botban
NBalazs — 02/22/2024 5:49 PM
Most adta el de csak nem küldi telegramra
bnc — 02/22/2024 5:49 PM
hat en nem vagom mit csinal
lehet stoppolnod kellene ssh-n aztan startolni telegrambol 
hatha eszhezter
NBalazs — 02/22/2024 5:51 PM
Image
Ennyit ír csak
bnc — 02/22/2024 5:52 PM
mi a fasz xdd
es elindult?
NBalazs — 02/22/2024 5:52 PM
Aha
bnc — 02/22/2024 5:53 PM
hat en nem vagom mi bugolt el akkor xddd
NBalazs — 02/22/2024 6:00 PM
Ó mindegy le is szarom, a lényeg hogy megy
NBalazs — 02/23/2024 7:56 AM
Image
Megjavult
Csinaltam egy uj telegram botot amit hozzaadtam a hummingbothoz es ezzel megjavult a regi
Nem ertem de mindegy xdd
bnc — 02/23/2024 8:49 AM
xdddd hat en nem vagom mi tortenik
nalam semmi ilyen nem fordult elo 1x se xddd
NBalazs — 02/23/2024 8:50 AM
A lényeg hogy megyen szépen
bnc — 02/23/2024 8:50 AM
na kiraly, remelem profitot is termel
NBalazs — 02/23/2024 8:51 AM
Dehogy xd
Most pont kurvaszar a market, összevissza ugrál
De nem vész
NBalazs — 02/25/2024 11:33 AM
Image
Dikk
Ez mit probalgatja
bnc — 02/25/2024 11:41 AM
xddd nemtudom
nekem nem csinalt ilyet
﻿
from hummingbot.strategy.script_strategy_base import ScriptStrategyBase
from hummingbot.connector.connector_base import ConnectorBase
from hummingbot.core.data_type.common import OrderType
from hummingbot.strategy.strategy_py_base import (
    BuyOrderCompletedEvent,
    BuyOrderCreatedEvent,
    OrderFilledEvent,
    SellOrderCompletedEvent,
    SellOrderCreatedEvent,
    MarketOrderFailureEvent,
)
from decimal import *
import time
import logging
class TambaScript(ScriptStrategyBase):
    #NE VALTOZTASD CSAK HA MASIK BASE KRIPTOT AKARSZ HASZNALNI
    base = "USDT"
    #VALTOZTASD ARRA AMELYIK KRIPTOT AKAROD TRADELNI
    crypto = "AI"
    #HA NEM TESTNET AKKOR IRD AT exchange = "binance" RE
    exchange = "binancetestnet"

    markets = {exchange: {f"{crypto}-{base}"}}
    
    
    boughtCrypto = False
    soldCrypto = False
    filledBuy = False
    filledSell = False
    #IRD AT A ZAROJELBE LEVO ERTEKET ARRA HOGY HANY SZAZALEKOS THRESHOLDDAL MUKODJON
    threshold = Decimal(0.02)
    peakPrice = 0
    basePrice = 0
    sellPrice = 0
    #CSAK A 99%AT HASZNALJA A BALANCENAK HOGY MINDIG LEGYEN PUFFER MERT NEHA BUGOL, DE HA KISERLETEZNI AKARSZ CSAPD FEL 100RA
    percentageOfBalance = 99
    buyinit = True
    sellinit = True
    boughtAmount = 0
    balance = 0
    

    def on_tick(self):
        if self.buyinit:
            self.boughtAmount = 0
            currentPrice = self.connectors[self.exchange].get_mid_price(f"{self.crypto}-{self.base}")
            self.balance = self.connectors[self.exchange].get_balance(self.base) * Decimal((self.percentageOfBalance/100))
            msg = f"Starting balance:{self.balance}"
            self.logger().info(msg)
            self.notify_hb_app_with_timestamp(msg)
            self.peakPrice = currentPrice
            self.basePrice = currentPrice
            if not currentPrice.is_nan():
                self.buyinit = False
        
        if not self.filledBuy:
            currentPrice = self.connectors[self.exchange].get_mid_price(f"{self.crypto}-{self.base}")
            msg = f"BUY PHASE --  Current price:{currentPrice} BuyPrice:{self.basePrice + (self.basePrice * self.threshold / 100)}"
            self.logger().info(msg)
            if currentPrice > self.peakPrice:
                self.peakPrice = currentPrice
            if currentPrice < self.basePrice:
                self.basePrice = currentPrice
                self.peakPrice = currentPrice
            if self.peakPrice >= self.basePrice + (self.basePrice * self.threshold / 100):
                msg = f"Buying crypto at this price -> {currentPrice}"
                amount = self.connectors[self.exchange].get_balance(self.base) * Decimal((self.percentageOfBalance/100)) / currentPrice
                self.logger().info(msg)
                self.notify_hb_app_with_timestamp(msg)
                self.buy(
                    connector_name=self.exchange,
                    trading_pair=f"{self.crypto}-{self.base}",
                    amount=Decimal(amount),
                    order_type=OrderType.MARKET,
                    price=Decimal(currentPrice)
                )
                self.boughtCrypto = True
                
        if self.filledBuy and not self.filledSell:
            if self.sellinit:
                msg = f"Entering selling phase!"
                self.logger().info(msg)
                self.notify_hb_app_with_timestamp(msg)
                currentPrice = self.connectors[self.exchange].get_mid_price(f"{self.crypto}-{self.base}")
                self.basePrice = currentPrice
                self.sellPrice = self.basePrice - (self.basePrice * self.threshold / 100)
                if not currentPrice.is_nan():
                    self.sellinit = False
            currentPrice = self.connectors[self.exchange].get_mid_price(f"{self.crypto}-{self.base}")
            assetBalance = self.connectors[self.exchange].get_balance(self.crypto)
            if assetBalance != self.boughtAmount:
                self.boughtAmount = assetBalance
            msg = f"SELL PHASE --  Current price:{currentPrice} SellPrice:{self.sellPrice}"
            self.logger().info(msg)
            if currentPrice > self.basePrice:
                self.basePrice = currentPrice
                self.sellPrice = self.basePrice - (self.basePrice * self.threshold / 100)
            if currentPrice <= self.sellPrice:
                msg = f"Selling crypto at this price -> {currentPrice}"
                self.logger().info(msg)
                self.notify_hb_app_with_timestamp(msg)
                self.sell(
                    connector_name=self.exchange,
                    trading_pair=f"{self.crypto}-{self.base}",
                    amount=Decimal(self.boughtAmount),
                    order_type=OrderType.MARKET,
                    price=Decimal(currentPrice)
                )
                self.soldCrypto = True
                
        if self.filledBuy == True and self.filledSell == True:
            self.filledBuy = False
            self.filledSell = False
            self.buyinit = True
            self.sellinit = True
            
    def did_complete_buy_order(self, event: BuyOrderCompletedEvent):
        msg = (f"Order {event.order_id} to buy {event.base_asset_amount} of {event.base_asset} is completed.")
        self.boughtAmount = event.base_asset_amount
        self.filledBuy = True
        self.log_with_clock(logging.INFO, msg)
        self.notify_hb_app_with_timestamp(msg)

    def did_complete_sell_order(self, event: SellOrderCompletedEvent):
        msg = (f"Order {event.order_id} to sell {event.base_asset_amount} of {event.base_asset} is completed.")
        self.filledSell = True
        self.log_with_clock(logging.INFO, msg)
        self.notify_hb_app_with_timestamp(msg)

    def did_create_buy_order(self, event: BuyOrderCreatedEvent):
        msg = (f"Created BUY order {event.order_id}")
        self.log_with_clock(logging.INFO, msg)
        self.notify_hb_app_with_timestamp(msg)

    def did_create_sell_order(self, event: SellOrderCreatedEvent):
        msg = (f"Created SELL order {event.order_id}")
        self.log_with_clock(logging.INFO, msg)
        self.notify_hb_app_with_timestamp(msg)
        
    def did_fill_order(self, event: OrderFilledEvent):
        if not self.filledBuy:
            self.boughtAmount += event.amount
            msg = (f"Buy order {event.order_id} is filled with amount {event.amount}")
            self.log_with_clock(logging.INFO, msg)
            self.notify_hb_app_with_timestamp(msg)
        else:
            self.boughtAmount -= event.amount
            msg = (f"Sell order {event.order_id} is filled with amount {event.amount}")
            self.log_with_clock(logging.INFO, msg)
            self.notify_hb_app_with_timestamp(msg)
    
    
    def did_fail_order(self, event: MarketOrderFailureEvent):
        if self.filledBuy is True and self.filledSell is False:
            if self.boughtAmount == 0:
                self.filledSell = True
            msg = (f"Order {event.order_id} to sell is completed but with errors, check logs!")
            self.log_with_clock(logging.INFO, msg)
            self.notify_hb_app_with_timestamp(msg)
        if self.filledBuy is False and self.boughtAmount > 0:
            self.filledBuy = True
            msg = (f"Order {event.order_id} to buy is completed and bought amount {self.boughtAmount} but with errors, check logs!")
            self.log_with_clock(logging.INFO, msg)
            self.notify_hb_app_with_timestamp(msg)
