from model import Batch, OrderLine, allocate
from datetime import date
import pytest


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL_TABLE", qty = 20, eta=date.Today())
    line = OrderLine("order-ref", "SMALL_TABLE", 2)
    batch.allocate(line)
    assert batch.available_quantity == 18


def make_batch_and_line(sku, batch_qty, line_qty):
    return (Batch("batch-001", sku, batch_qty, eta = date.today()), OrderLine("order-123", sku, line_qty))

def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)
    assert small_batch.can_allocate(large_line) is False

def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 2, 2)
    assert batch.can_allocate(line)

def test_can_allocate_if_skus_dont_match():
    batch = Batch("batch-001", "GOODNT-CHAIR", 100, eta=None)
    different_sku_line = OrderLine("order-123", "EXPENSIVE-TOASTER", 10)
    assert batch.can_allocate(different_sku_line) is False

def test_can_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("DECORATIVE-OTTOMAN", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20

def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ANGULAR-DESK", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18

def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "CYBERPUNK-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "CYBERPUNK-CLOCK", 100, eta=tomorrow)
    line = OrderLine("oref", "CYBERPUNK-CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100

def test_prefers_earlier_batches():
    earliest = Batch("speedy-batch", "MINIMALIST-FORK", 100, eta=today)
    medium = Batch("normal-batch", "MINIMALIST-FORK", 100, eta=tomorrow)
    latest = Batch("slow-batch", "MINIMALIST-FORK", 100, eta=later)
    line = OrderLine("order1", "MINIMALIST-FORK", 10)

    allocate(line, [medium, earliest, latest])
    
    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100

def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch-ref", "RT-POSTER", 100, eta=none)
    shipment_batch = Batch("shipment-batch-ref", "RT-POSTER", 100, eta=tomorrow)
    line = OrderLine("oref", "RT-POSTER", 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("batch1", "SMALL-CHUNGUS", 10, eta=today)
    allocate(OrderLine("order1", "SMALL-CHUNGUS", 10), batch)

    with pytest.raises(OutOfStock, match="SMALL-CHUNGUS"):
        allocate(OrderLine("order2", "SMALL-CHUNGUS", 1), [batch])