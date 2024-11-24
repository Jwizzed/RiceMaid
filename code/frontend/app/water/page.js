"use client";
import React, { useState, useEffect } from "react";
import { Footer } from "@/components/Footer";
import { useRouter } from "next/navigation";
import RainfallTable from "@/components/WaterChart";

export default function WaterPage() {
  const [data, setData] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [averageCapacity, setAverageCapacity] = useState(0);
  const itemsPerPage = 10;
  const pageWindowSize = 5; // Number of page numbers to display
  const router = useRouter();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(
          "https://api.dwr.go.th/twsapi/v1.0/SmallsizedWaterResourcesInfo/",
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer NGI2ODk0ZDY1MTVkNmRhMmQ1ZGU0N2YyYWM3MGNkNzk4MmZkNTExOTEyNjJmZjRlMmJmNTU2ZGFlMTBiYjQxNA==`,
            },
          }
        );
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        setData(result.waterResources);

        // Calculate the average capacity
        const capacities = result.waterResources.map(
          (resource) => resource.waterResourcesMetadata.capacity
        );
        const totalCapacity = capacities.reduce(
          (acc, capacity) => acc + capacity,
          0
        );
        const average = totalCapacity / capacities.length;
        setAverageCapacity(average);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = data.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(data.length / itemsPerPage);

  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  // Calculate the start and end of the pagination window
  const startPage = Math.max(1, currentPage - Math.floor(pageWindowSize / 2));
  const endPage = Math.min(totalPages, startPage + pageWindowSize - 1);

  return (
    <div className="min-h-screen bg-white font-sans">
      <header className="sticky top-0 z-10 bg-white p-4 border-b">
        <div className="flex items-center justify-between">
          <span className="text-sm">Rice maid</span>
          <span className="bg-yellow-400 text-xs px-2 py-1 rounded-full">
            FAQ
          </span>
        </div>
      </header>

      <main className="p-6 space-y-6">
        <section className="space-y-2 gap-2 flex flex-col justify-center items-center">
          <>
            <h1 className="text-[32px] font-bold">Rice Farming</h1>
            <h1 className="text-[32px] font-bold">Essentials</h1>
          </>
          <>
            <p className="text-[20px] text-gray-600">
              Discover the Secrets to Successful
            </p>
            <p className="text-[20px] text-gray-600">Rice Cultivation</p>
          </>
          <button
            onClick={() => router.push("https://www.ricethailand.go.th/")}
            className="w-full bg-[#FFD903] h-[44px] rounded-[22px] text-[#51470D] font-bold"
          >
            Learn more
          </button>
        </section>

        <section>
          <h1 className="text-[42px] font-semibold mb-4">Water Resources</h1>
          <div className="mb-4">
            <p className="text-lg font-semibold">
              Average Capacity: {averageCapacity.toFixed(2)} Million Cubic
              Meters
            </p>
          </div>
          <table className="min-w-full bg-white border">
            <thead>
              <tr>
                <th className="py-2 px-4 border-b">Name</th>
                <th className="py-2 px-4 border-b">
                  Capacity (Million Cubic Meters)
                </th>
              </tr>
            </thead>
            <tbody>
              {currentItems.map((resource, index) => (
                <tr key={index}>
                  <td className="py-2 px-4 border-b">
                    {resource.waterResourcesMetadata.waterResourcesName}
                  </td>
                  <td className="py-2 px-4 border-b">
                    {resource.waterResourcesMetadata.capacity}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="flex justify-center mt-4 flex-wrap">
            {Array.from({ length: endPage - startPage + 1 }, (_, index) => (
              <button
                key={index}
                onClick={() => handlePageChange(startPage + index)}
                className={`mx-1 px-3 py-1 border rounded ${
                  currentPage === startPage + index
                    ? "bg-blue-500 text-white"
                    : "bg-white text-blue-500"
                }`}
              >
                {startPage + index}
              </button>
            ))}
          </div>
          <div className="relative flex flex-row item-center gap-4 mt-4 mb-4">
            <img
              src="/images/rice2.jpeg"
              alt="Rice Field"
              className="object-cover rounded-[22px]"
            />
          </div>
          <RainfallTable />
        </section>
        <Footer />
      </main>
    </div>
  );
}
