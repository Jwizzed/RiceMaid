"use client";
import React, { useState, useEffect } from "react";
import { mockRainfallData } from "./MockData"; // Adjust the path as necessary

export default function RainfallTable() {
const [rainfallData, setRainfallData] = useState([]);
const [currentPage, setCurrentPage] = useState(1);
const itemsPerPage = 10;

useEffect(() => {
  // Simulate fetching data by directly using the mock data
  setRainfallData(mockRainfallData);
}, []);

// Calculate the indices for slicing the data
const indexOfLastItem = currentPage * itemsPerPage;
const indexOfFirstItem = indexOfLastItem - itemsPerPage;
const currentItems = rainfallData.slice(indexOfFirstItem, indexOfLastItem);
const totalPages = Math.ceil(rainfallData.length / itemsPerPage);

const handlePageChange = (pageNumber) => {
  setCurrentPage(pageNumber);
};

return (
  <div className="min-h-screen bg-white font-sans">
    <h1 className="text-2xl font-bold mb-4 text-black">Rainfall Data</h1>
    <table className="min-w-full bg-white border">
      <thead>
        <tr>
          <th className="py-2 px-4 border-b text-black">Province</th>
          <th className="py-2 px-4 border-b text-black">Date</th>
          <th className="py-2 px-4 border-b text-black">Rainfall Mean</th>
        </tr>
      </thead>
      <tbody>
        {currentItems.map((entry, index) => (
          <tr key={index}>
            <td className="py-2 px-4 border-b text-black">
              {entry.prov_name_th}
            </td>
            <td className="py-2 px-4 border-b text-black">{entry.date}</td>
            <td className="py-2 px-4 border-b text-black">
              {entry.rainfall_mean.toFixed(4)}
            </td>
          </tr>
        ))}
      </tbody>
    </table>

    <div className="flex justify-center mt-4 flex-wrap">
      {Array.from({ length: totalPages }, (_, index) => (
        <button
          key={index}
          onClick={() => handlePageChange(index + 1)}
          className={`mx-1 px-3 py-1 border rounded ${
            currentPage === index + 1
              ? "bg-blue-500 text-white"
              : "bg-white text-blue-500"
          }`}
        >
          {index + 1}
        </button>
      ))}
    </div>
  </div>
);
}