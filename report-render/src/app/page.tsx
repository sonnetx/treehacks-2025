"use client";

import { BarChart } from "@mui/x-charts/BarChart";
import { PieChart } from "@mui/x-charts/PieChart";
import { Lightbulb, Factory, Car } from "lucide-react";
import { useEffect, useState } from "react";

export default function CarbonEmissionsReport() {
  const currentDate = new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  const [data, setData] = useState(null);

  useEffect(() => {
    fetch("/api/reportData") // Calls the Next.js API
      .then((res) => res.json())
      .then((data) => {
        setData(data.data.report_data); // ✅ Set state
        console.log(data.message); // ✅ Log message properly
      })
      .catch((error) => console.error("Error fetching data:", error));
  }, []);

  useEffect(() => {
    console.log(data);
  }, [data]);

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <main className="container mx-auto bg-white shadow-lg rounded-lg overflow-hidden">
        <header className="bg-gray-800 text-white p-6">
          <h1 className="text-3xl font-bold">Annual Carbon Emissions Report</h1>
          <p className="text-gray-300 mt-2">Generated on {currentDate}</p>
        </header>

        <div className="p-6 space-y-8">
          <section>
            <h2 className="text-2xl font-semibold mb-4 text-black">
              Executive Summary
            </h2>
          </section>
          <section>
            <PieChart
              series={[
                {
                  data: data
                    ? [
                        { id: 0, value: data.numTrash ?? 0, label: "Trash" },
                        {
                          id: 1,
                          value: data.numCompost ?? 0,
                          label: "Compose",
                        },
                        {
                          id: 2,
                          value: data.numRecycle ?? 0,
                          label: "Recycle",
                        },
                      ]
                    : [],
                },
              ]}
              width={400}
              height={200}
            />
          </section>
          <section>
            <h2 className="text-2xl font-semibold mb-4 text-black">
              Total Emissions
            </h2>

            <div className="grid grid-cols-2 gap-4">
              {/* Box for Total Emissions Number */}
              <div className="flex flex-col items-center justify-center bg-gray-100 rounded-md p-6 gap-2">
                <p className="text-2xl font-semibold text-black">
                  Total Emissions
                </p>
                <span className="text-6xl font-bold text-blue-600">123.45</span>
                <p className="text-lg text-gray-500">Metric Tons CO2e</p>
              </div>

              {/* Box for Bar Chart */}
              <div className="bg-gray-100 rounded-md p-6 flex items-center justify-center">
                <div className="flex flex-col items-center justify-center">
                  <BarChart
                    xAxis={[
                      {
                        scaleType: "band",
                        data: ["2020", "2021", "2022", "2023"],
                      },
                    ]}
                    series={[{ data: [50, 75, 100, 125] }]}
                    width={400}
                    height={300}
                  />
                  <p className="text-sm text-gray-500 mt-2 text-center">
                    Chart: Annual Carbon Emissions (metric tons CO2e)
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* <section>
            <h2 className="text-2xl font-semibold mb-4 text-black">
              Emissions by Source
            </h2>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <div>
                <div className="flex flex-row items-center justify-between pb-2 space-y-0">
                  <div className="text-sm text-black font-medium">
                    Electricity
                  </div>
                  <Lightbulb className="w-4 h-4 text-gray-500" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-black">45%</div>
                  <div className="mt-2" />
                </div>
              </div>
              <div>
                <div className="flex flex-row items-center justify-between pb-2 space-y-0">
                  <div className="text-sm font-medium text-black">
                    Manufacturing
                  </div>
                  <Factory className="w-4 h-4 text-gray-500" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-black">30%</div>
                  <div className="mt-2" />
                </div>
              </div>
              <div>
                <div className="flex flex-row items-center justify-between pb-2 space-y-0">
                  <div className="text-sm font-medium text-black">
                    Transportation
                  </div>
                  <Car className="w-4 h-4 text-gray-500" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-black">25%</div>
                  <div className="mt-2" />
                </div>
              </div>
            </div>
          </section> */}
          {/* Compostable & Recyclable Components Section */}
          <section className="bg-gray-50 rounded-lg p-6 shadow-md">
            <h2 className="text-2xl font-semibold mb-4 text-black text-center">
              Waste Breakdown
            </h2>

            <div className="grid grid-cols-2 gap-6">
              {/* Compostable Components */}
              <div className="bg-green-100 p-4 rounded-md shadow-md">
                <h3 className="text-lg font-semibold text-green-800 flex items-center gap-2">
                  🌱 Compostable Components
                </h3>
                {data?.compostNames?.length > 0 ? (
                  <ul className="list-disc pl-5 mt-2 text-gray-700">
                    {data.compostNames.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500 mt-2">
                    No compostable components reported.
                  </p>
                )}
              </div>

              {/* Recyclable Components */}
              <div className="bg-blue-100 p-4 rounded-md shadow-md">
                <h3 className="text-lg font-semibold text-blue-800 flex items-center gap-2">
                  ♻️ Recyclable Components
                </h3>
                {data?.recycleNames?.length > 0 ? (
                  <ul className="list-disc pl-5 mt-2 text-gray-700">
                    {data.recycleNames.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500 mt-2">
                    No recyclable components reported.
                  </p>
                )}
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4 text-black">
              Reduction Strategies
            </h2>
            <ul className="list-disc pl-5 space-y-2 text-gray-600">
              <li>Implement energy-efficient lighting across all facilities</li>
              <li>Increase use of renewable energy sources</li>
              <li>Optimize manufacturing processes to reduce waste</li>
              <li>Encourage remote work to decrease commuting emissions</li>
              <li>Invest in electric vehicles for company fleet</li>
            </ul>
          </section>
        </div>

        <footer className="bg-gray-100 p-6 mt-8">
          <p className="text-sm text-gray-600 text-center">
            This report was generated using verified data sources and follows
            the GHG Protocol Corporate Standard. For more information, please
            contact our sustainability team.
          </p>
        </footer>
      </main>
    </div>
  );
}
