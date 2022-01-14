// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/vendor/SafeMathChainlink.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase, Ownable {
    using SafeMathChainlink for uint256;

    address payable[] public players;
    uint256 public usdEntenanceFee;
    uint256 public randomness;
    uint256 public winnerIndex;
    AggregatorV3Interface internal ethUsdPrice;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lotteryState;
    uint256 public fee;
    bytes32 public keyHash;
    address payable public recentWinner;
    event RequestedRandomness(bytes32 requestId);
    event CalculatingWinner(address addy);

    constructor(
        address _priceFeed,
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyHash
    ) public VRFConsumerBase(_vrfCoordinator, _link) {
        usdEntenanceFee = 50 * (10**18);
        ethUsdPrice = AggregatorV3Interface(_priceFeed);
        lotteryState = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyHash = _keyHash;
    }

    function enter() public payable {
        require(lotteryState == LOTTERY_STATE.OPEN);
        require(
            msg.value >= getEnteranceFee(),
            "EnteranceFee must be greater than "
        );
        players.push(msg.sender);
    }

    function getEnteranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPrice.latestRoundData();
        uint256 adjustedPrice = uint256(price) * 10**10;
        uint256 costToEnter = (usdEntenanceFee * 10**18) / adjustedPrice;
        return costToEnter;
    }

    function startLottery() public onlyOwner {
        require(
            lotteryState == LOTTERY_STATE.CLOSED,
            "cannot start a new lottery yet!"
        );
        lotteryState = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        lotteryState = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyHash, fee);
        emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        randomness = _randomness;
        require(
            lotteryState == LOTTERY_STATE.CALCULATING_WINNER,
            "You aren't there yet!"
        );

        require(_randomness > 0, "random-not-found");
        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        emit CalculatingWinner(recentWinner);
        recentWinner.transfer(address(this).balance);
        // Reset
        players = new address payable[](0);
        lotteryState = LOTTERY_STATE.CLOSED;
    }
}
