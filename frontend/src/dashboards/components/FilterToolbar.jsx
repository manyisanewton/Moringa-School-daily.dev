import React from "react";
import './FilterToolbar.css';
import { FaSearch, FaChevronDown } from 'react-icons/fa';

const FilterToolbar = () => {
    return (
        <div className="filter-toolbar">
            <div className="filters">
                <button className="filter-btn">All <FaChevronDown /></button>
                <button className="filter-btn">Drafts</button>
                <button className="filter-btn">Published</button>
                <button className="filter-btn">Flagged</button>
            </div>
            <div className="search-func">
                <select className="sort-dropdown">
                    <option value="sort-by-newest">Sort by: Newest</option>
                    <option value="sort-by-oldest">Sort by: Oldest</option>
                </select>
                <div className="search-bar">
                    <input type="text" placeholder="Search Content..."/>
                    <FaSearch className="search-icon" />
                </div>
            </div>
        </div>
    );
};

export default FilterToolbar;