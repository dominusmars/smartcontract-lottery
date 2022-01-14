from brownie import Lottery, config, network
from scripts.helper_functions import get_account, get_contract, fund_contract_with_link
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price").address,
        get_contract("vrf_coordinator"),
        get_contract("link_token"),
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("deployed Lottery")
    print(lottery.address)
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    tx_start = lottery.startLottery({"from": account})
    tx_start.wait(1)
    print("lottery started")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEnteranceFee() + 100000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("lottery entered")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]

    fund_contract_with_link(lottery.address)

    tx = lottery.endLottery()
    tx.wait(1)
    time.sleep(60)
    print("lottery ended")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
