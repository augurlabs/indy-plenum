import logging

import pytest

from plenum.common.messages.node_messages import CatchupReq
from stp_core.common.log import getlogger
from plenum.test.helper import sdk_send_random_and_check

logger = getlogger()
leger_id = 1


def test_receive_incorrect_catchup_request_with_end_greater_catchuptill(looper,
                                                                        txnPoolNodeSet,
                                                                        sdk_pool_handle,
                                                                        sdk_wallet_client,
                                                                        monkeypatch):
    end = 15
    catchup_till = 10

    def _check_discard(msg, reason, logMethod=logging.error, cliOutput=False):
        assert reason.find("not able to service since "
                           "end = {} greater then "
                           "catchupTill = {}".format(end, catchup_till))

    req = CatchupReq(leger_id, 0, end, catchup_till)
    _process_catchup_req(req,
                         _check_discard,
                         looper,
                         txnPoolNodeSet,
                         sdk_pool_handle,
                         sdk_wallet_client,
                         monkeypatch)


def test_receive_incorrect_catchup_request_with_start_greater_end(looper,
                                                                  txnPoolNodeSet,
                                                                  sdk_pool_handle,
                                                                  sdk_wallet_client,
                                                                  monkeypatch):
    start = 10
    end = 5

    def _check_discard(msg, reason, logMethod=logging.error, cliOutput=False):
        assert reason.find("not able to service since "
                           "start = {} greater then "
                           "end = {}"
                           .format(start, end))

    req = CatchupReq(leger_id, start, end, 11)
    _process_catchup_req(req,
                         _check_discard,
                         looper,
                         txnPoolNodeSet,
                         sdk_pool_handle,
                         sdk_wallet_client,
                         monkeypatch)


def test_receive_incorrect_catchup_request_with_catchuptill_greater_ledger_size(
        looper,
        txnPoolNodeSet,
        sdk_pool_handle,
        sdk_wallet_client,
        monkeypatch):
    catchup_till = 100
    req = CatchupReq(leger_id, 0, 10, catchup_till)
    ledger_size = txnPoolNodeSet[0].ledgerManager.getLedgerForMsg(req).size

    def _check_discard(msg, reason, logMethod=logging.error, cliOutput=False):
        assert reason.find("not able to service since "
                           "catchupTill = {} greater then "
                           "ledger size = {}"
                           .format(catchup_till, ledger_size))

    _process_catchup_req(req,
                         _check_discard,
                         looper,
                         txnPoolNodeSet,
                         sdk_pool_handle,
                         sdk_wallet_client,
                         monkeypatch)


def _process_catchup_req(req: CatchupReq,
                         check_discard,
                         looper,
                         txnPoolNodeSet,
                         sdk_pool_handle,
                         sdk_wallet_client,
                         monkeypatch):
    sdk_send_random_and_check(looper,
                              txnPoolNodeSet,
                              sdk_pool_handle,
                              sdk_wallet_client,
                              4)
    ledger_manager = txnPoolNodeSet[0].ledgerManager
    monkeypatch.setattr(ledger_manager.owner, 'discard', check_discard)
    ledger_manager.processCatchupReq(req, "frm")
