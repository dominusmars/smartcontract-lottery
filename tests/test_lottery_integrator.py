from brownie import network
import pytest
import time
from scripts.deploy_lottery import deploy_lottery
from scripts.helper_functions import (
    LOCAL_BLOCKCHAIN_DEPLOYMENTS,
    fund_contract_with_link,
    get_account,
)


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_DEPLOYMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEnteranceFee() + 100000})
    lottery.enter({"from": account, "value": lottery.getEnteranceFee() + 100000})
    fund_contract_with_link(lottery)
    lottery.endLottery({"from": account})
    time.sleep(60)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
