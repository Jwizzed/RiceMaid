"use client";
import React, { useState, useEffect } from "react";
import { Footer } from "@/components/Footer";
import { useRouter } from "next/navigation";

export default function WeatherForecast() {
  const [forecastData, setForecastData] = useState([]);
  const [region, setRegion] = useState("E"); // Default region is East
  const router = useRouter();

  useEffect(() => {
    const fetchWeatherData = async () => {
      try {
        const response = await fetch(
          `https://data.tmd.go.th/nwpapi/v1/forecast/location/daily/region?region=${region}&fields=tc_max,rh&date=2024-11-23&duration=2`,
          {
            method: "GET",
            headers: {
              accept: "application/json",
              authorization:
                "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjY4YzM0ZTljYTFmZWMzMGRmNGVjMjYyOWUyNjE4MmFjYTdhZWE2ZTU1M2Y3NzUxZjcwZGM1ZTdlZjZhNjI3OGY3MGFkZjU3MjNlY2JjM2JjIn0.eyJhdWQiOiIyIiwianRpIjoiNjhjMzRlOWNhMWZlYzMwZGY0ZWMyNjI5ZTI2MTgyYWNhN2FlYTZlNTUzZjc3NTFmNzBkYzVlN2VmNmE2Mjc4ZjcwYWRmNTcyM2VjYmMzYmMiLCJpYXQiOjE3MzIzNDk5NDcsIm5iZiI6MTczMjM0OTk0NywiZXhwIjoxNzYzODg1OTQ3LCJzdWIiOiIzNTY4Iiwic2NvcGVzIjpbXX0.N93GyFxSaAglOqsUYlxxEM2SvrtQ8FmZtJ4o7LHAQV6svEqY8se7_ayeHnW4KUqzugOQj-oOB7PyZwZsIJHhhaqWVtpGxglqYDaUi0osQLYbr5wKl3BHJP66lIa2hSM90qTX24hXGOMmeL0vnoUR-Oiu9oEEmqlT7crWjLzK2bbQ86p3clMxHlucjIdJws-R9LdZiOugBB8V6TRgmgR4A4Da9QBPRYI67q35d1mHtEtHI86u1emK3eh084un3B1aSOXY7aNvAezj81x9nNEU0O96nlsE_IojDam_vgnJ5f_1Ajj3w9VDSdrT7HOoi0Yo35pfF6paXyw57JFYnKEKk9TatHb0tiWluKH_r8M2kZX7AASg-egwWytmcobijndkDfyXUpbbhK-bbE5kX1vKHHL-J9gC_ZqyEnZyRHxJ3SPBsbvlX96zDHWOKa_hzdmNG1dtTE4rla_5KmMQIX4RNhC6iiogn-JL8uT-1WtlPpfHqaNdeFzUpAuiGZKz0B293InpoklfKbiA6cwjnOIZvK7VgW-rLBtbAU1iZk6-9E7R9VdnMkL2MUpSMRMYgNF20FbqSBU6dNAtDeCtp5RsvdsD0dcd-BEIM0YzYQ0EJvmUisBp2szp68Djg4hRI-w2fzKf-LxG1Ks6OBskyzWSBEM9-e5SIYBKCviDOvpdegU", // Replace with your actual token
            },
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        setForecastData(result.WeatherForecasts);
      } catch (error) {
        console.error("Error fetching weather data:", error);
      }
    };

    fetchWeatherData();
  }, [region]); // Re-fetch data when the region changes

  // Function to format the date
  const formatDate = (dateTimeString) => {
    const date = new Date(dateTimeString);
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, "0");
    const day = date.getDate().toString().padStart(2, "0");
    return `${year}-${month}-${day}`;
  };

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
        <div className="relative flex flex-row item-center gap-4 mt-4 mb-4">
          <img
            src="/images/rice3.jpeg"
            alt="Rice Field"
            className="object-cover rounded-[22px]"
          />
        </div>
        <section>
          <h1 className="text-xl font-bold mb-4">Weather Forecast</h1>
          <div className="mb-4">
            <label htmlFor="region" className="mr-2">
              Select Region:
            </label>
            <select
              id="region"
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="border p-2 rounded w-full"
            >
              <option value="C">Center</option>
              <option value="N">North</option>
              <option value="E">East</option>
              <option value="NE">NorthEast</option>
              <option value="W">West</option>
              <option value="S">South</option>
            </select>
          </div>
          <table className="min-w-full bg-white border">
            <thead>
              <tr>
                <th className="py-2 px-4 border-b">Province</th>
                <th className="py-2 px-4 border-b">Date</th>
                <th className="py-2 px-4 border-b">Max Temp (°C)</th>
                <th className="py-2 px-4 border-b">Humidity (%)</th>
              </tr>
            </thead>
            <tbody>
              {forecastData.map((location, index) =>
                location.forecasts.map((forecast, fIndex) => (
                  <tr key={`${index}-${fIndex}`}>
                    <td className="py-2 px-4 border-b">
                      {location.location.province}
                    </td>
                    <td className="py-2 px-4 border-b">
                      {formatDate(forecast.time)}
                    </td>
                    <td className="py-2 px-4 border-b">
                      {forecast.data.tc_max}
                    </td>
                    <td className="py-2 px-4 border-b">{forecast.data.rh}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </section>

        <Footer />
      </main>
    </div>
  );
}
