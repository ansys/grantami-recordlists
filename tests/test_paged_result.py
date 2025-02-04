# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Any, Iterator, List, Type

import pytest

from ansys.grantami.recordlists._models import AuditLogItem, PagedResult


class TestPagedResult:
    @pytest.mark.parametrize(
        ("item_type", "expected_type_string"),
        [
            (int, "int"),
            (str, "str"),
            (bool, "bool"),
            (float, "float"),
            (AuditLogItem, "AuditLogItem"),
        ],
    )
    @pytest.mark.parametrize("page_size", [1, 10, 100, 1000])
    def test_repr(self, item_type: Type, expected_type_string: str, page_size: int):
        def next_func(page_size: int, start_index: int) -> List[Any]:
            raise NotImplementedError()

        paged_result = PagedResult(next_func, item_type, page_size=page_size)
        assert (
            paged_result.__repr__()
            == f"<PagedResult[{expected_type_string}] page_size={page_size}>"
        )

    def test_no_results_raises_stop_iteration(self):
        call_count = 0

        def next_func(page_size: int, start_index: int) -> List[int]:
            nonlocal call_count
            call_count += 1
            return []

        paged_result = PagedResult(next_func, int, 10)

        with pytest.raises(StopIteration):
            next(paged_result)
        assert call_count == 1

    def test_error_in_next_func_falls_through(self):
        def next_func(page_size: int, start_index: int) -> List[int]:
            raise NotImplementedError()

        paged_result = PagedResult(next_func, int, 10)

        with pytest.raises(NotImplementedError):
            next(paged_result)

    def test_iterator_exposes_correct_number_of_values_when_total_is_less_than_page_size(self):
        call_count = 0

        def next_func(page_size: int, start_index: int) -> List[int]:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return [1, 2, 3]
            return []

        paged_result = PagedResult(next_func, int, 10)
        list_result = list(paged_result)

        assert (
            call_count == 2
        )  # Called once to retrieve the values and again to determine the end of the iterator has been reached
        assert list_result == [1, 2, 3]

    def test_iterator_exposes_correct_number_of_values_when_total_is_greater_than_page_size(self):
        call_count = 0

        def next_func(page_size: int, start_index: int) -> List[int]:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return [1, 2, 3]
            elif call_count == 2:
                return [4, 5]
            return []

        paged_result = PagedResult(next_func, int, 3)
        list_result = list(paged_result)

        assert (
            call_count == 3
        )  # Called twice to retrieve the values and again to determine the end of the iterator has been reached
        assert list_result == [1, 2, 3, 4, 5]

    def test_iter_return_iterator(self):
        def next_func(page_size: int, start_index: int) -> List[int]:
            raise NotImplementedError()

        paged_result = PagedResult(next_func, int, 10)

        iterator = iter(paged_result)
        assert isinstance(iterator, Iterator)

    def test_paged_result_can_be_iterated_over(self):
        call_count = 0

        def next_func(page_size: int, start_index: int) -> List[int]:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return [1, 2, 3]
            elif call_count == 2:
                return [4, 5]
            return []

        paged_result = PagedResult(next_func, int, 3)

        result = []
        for value in paged_result:
            result.append(value)

        assert (
            call_count == 3
        )  # Called twice to retrieve the values and again to determine the end of the iterator has been reached
        assert result == [1, 2, 3, 4, 5]
