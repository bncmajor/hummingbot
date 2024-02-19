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
    crypto = "AVAX"
    #HA NEM TESTNET AKKOR IRD AT exchange = "binance" RE
    exchange = "binancetestnet"

    markets = {exchange: {f"{crypto}-{base}"}}
    
    
    boughtCrypto = False
    soldCrypto = False
    filledBuy = False
    filledSell = False
    #IRD AT A ZAROJELBE LEVO ERTEKET ARRA HOGY HANY SZAZALEKOS THRESHOLDDAL MUKODJON
    threshold = Decimal(2)
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
        

