// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "contracts/openzeppelin-contracts/contracts/access/Ownable.sol";
import "contracts/openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";

contract Subscription is Ownable {
    IERC20 public token;
    uint256 public cost;
    uint256 public subPeriodSec;
    mapping (address => uint256) public lastWithdrawTimestamp;

    constructor(address _token, uint256 _cost, uint256 _subPeriodSec) Ownable(msg.sender) {
        require(_token != address(0), "ERC20 address cannot be zero");
        token = IERC20(_token);
        cost = _cost;
        subPeriodSec = _subPeriodSec;
    }

    function withdrawMoney(address from) public {
        require(block.timestamp >= lastWithdrawTimestamp[from] + subPeriodSec || lastWithdrawTimestamp[from] == 0);
        lastWithdrawTimestamp[from] = block.timestamp;
        token.transferFrom(from, owner(), cost);
    }
}