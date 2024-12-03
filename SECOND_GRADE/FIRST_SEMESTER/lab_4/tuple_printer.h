#pragma once

#include <tuple>
#include <iostream>


template<typename Tuple, std::size_t Index>
struct TuplePrinter
{
    static void print(std::ostream& os, const Tuple& tuple)
    {
        TuplePrinter<Tuple, Index - 1>::print(os, tuple);
        os << ", " << std::get<Index>(tuple);
    }
};


template<typename Tuple>
struct TuplePrinter<Tuple, 0>
{
    static void print(std::ostream& os, const Tuple& tuple) { os << std::get<0>(tuple); }
};


template<typename... Args>
std::ostream& operator<<(std::ostream& os, const std::tuple<Args...>& tuple) {
    os << "(";
    if constexpr (sizeof...(Args) > 0)
        TuplePrinter<std::tuple<Args...>, sizeof...(Args) - 1>::print(os, tuple);

    os << ")";
    return os;
}