"use client";
import React, { useState, useEffect } from "react";
import { Footer } from "@/components/Footer";

export default function WeatherForecast() {
const [forecastData, setForecastData] = useState([]);
const [region, setRegion] = useState("E"); // Default region is East

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
      </section>
      <section>
        <div className="mb-4 bg-[#FFF3D5] p-4 rounded-[22px]">
        <h1 className="text-xl font-bold mb-4">
          ระเบียบวิธีลดก๊าซเรือนกระจกภาคสมัครใจ สำหรับ
          กิจกรรมการจัดการพื้นที่ปลูกข้าว
        </h1>
        <h1 className="text-xl font-bold mb-4">
          (Enhanced Good Practices in Paddy Rice Field)
        </h1>
        </div>
        <p>การปล่อยก๊าซเรือนกระจกในกรณีฐาน (Baseline emissions)</p>
        <ul className="list-disc pl-5">
          <li>ปริมาณการปล่อยก๊าซมีเทนจากพื้นที่ (Methane emissions from paddy fields)</li>
          <li>ปริมาณการปล่อยก๊าซคาร์บอนไดออกไซด์จากการใส่ปูน</li>
          <li>ปริมาณการปล่อยก๊าซคาร์บอนไดออกไซด์จากการใส่ปุ๋ยยูเรีย</li>
          <li>ปริมาณการปล่อยก๊าซไนตรัสออกไซด์จากการใส่ปุ๋ยไนโตรเจน</li>
        </ul>
        <div className="relative flex flex-row item-center gap-4 mt-4">
          <img
            src="/images/rice1.jpg"
            alt="Rice Field"
            className="object-cover rounded-[22px]"
          />
        </div>
        <a
          href="/Good Practices in Paddy Rice.pdf" // Replace with your actual file name
          download
          className="mt-4 w-full bg-[#FFD903] h-[44px] rounded-[22px] text-[#51470D] font-bold flex items-center justify-center"
        >
          Download the PDF
        </a>
      </section>

      <Footer />
    </main>
  </div>
);
}