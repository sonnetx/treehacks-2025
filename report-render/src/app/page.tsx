"use client";

import { BarChart } from "@mui/x-charts/BarChart";
import { PieChart } from "@mui/x-charts/PieChart";
import { Lightbulb, Leaf, Factory, Home, Car } from "lucide-react";
import { useEffect, useState } from "react";

export default function CarbonEmissionsReport() {
  const currentDate = new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  const [data, setData] = useState(null);

  useEffect(() => {
    fetch("/api/reportData")
      .then((res) => res.json())
      .then((data) => {
        setData(data.data.report_data);
        console.log(data.message);
      })
      .catch((error) => console.error("Error fetching data:", error));
  }, []);

  useEffect(() => {
    console.log(data);
  }, [data]);

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <main className="container mx-auto bg-white shadow-lg rounded-lg overflow-hidden">
        {/* Header */}
        <header className="bg-gray-800 text-white p-6 text-center">
          <h1 className="text-3xl font-bold">Ecological Footprint Report</h1>
          <p className="text-gray-300 mt-2">Generated on {currentDate}</p>
        </header>

        <div className="p-6 space-y-8">
          {/* Executive Summary & Total Emissions */}
          <section className="bg-white shadow-md rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 text-center text-black">
              Executive Summary & Total Emissions
            </h2>

            <div className="grid md:grid-cols-3 gap-6">
              {/* Pie Chart */}
              <div className="bg-gray-50 rounded-lg p-6 shadow-md flex flex-col items-center justify-center">
                <h3 className="text-lg font-semibold text-black mb-2">
                  Waste Breakdown
                </h3>
                <PieChart
                  series={[
                    {
                      data: data
                        ? [
                            {
                              id: 0,
                              value: data.numTrash ?? 0,
                              label: "Trash",
                            },
                            {
                              id: 1,
                              value: data.numCompost ?? 0,
                              label: "Compost",
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
                  width={250}
                  height={200}
                  legend={{
                    labelStyle: { fontSize: 12 },
                    padding: 10,
                  }}
                />
              </div>

              {/* Total Emissions */}
              <div className="bg-gray-50 rounded-lg p-6 shadow-md flex flex-col items-center justify-center">
                <p className="text-xl font-semibold text-black">
                  Total Emissions
                </p>
                <span className="text-5xl font-bold text-blue-600">
                  {data
                    ? Number(
                        parseFloat(data.recycleInTrashEmissions.toFixed(4) ?? 0)
                      ) +
                      Number(
                        parseFloat(data.compostInTrashEmissions.toFixed(4) ?? 0)
                      ) +
                      Number(parseFloat(data.trashEmissions.toFixed(4) ?? 0))
                    : "Loading..."}
                </span>
                <p className="text-lg text-gray-500">kg CO2e</p>
              </div>

              {/* Bar Chart */}
              <div className="bg-gray-50 rounded-lg p-6 shadow-md flex flex-col items-center justify-center">
                <h3 className="text-lg font-semibold text-black mb-2">
                  Emissions
                </h3>
                {data && (
                  <BarChart
                    xAxis={[
                      {
                        scaleType: "band",
                        data: ["Trash", "Recycle", "Compose"],
                      },
                    ]}
                    series={[
                      {
                        data: [
                          data.trashEmissions,
                          data.recycleInTrashEmissions,
                          data.compostInTrashEmissions,
                        ],
                      },
                    ]}
                    width={300}
                    height={250}
                  />
                )}
                <p className="text-sm text-gray-500 mt-2 text-center">
                  Annual Carbon Emissions (metric tons CO2e)
                </p>
              </div>
            </div>
          </section>

          {/* Waste Breakdown */}
          <section className="bg-white rounded-lg p-6 shadow-md">
            <h2 className="text-2xl font-semibold mb-4 text-center text-black">
              Waste Breakdown
            </h2>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Compostable Components */}
              <div className="bg-green-100 p-6 rounded-lg shadow-md">
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
              <div className="bg-blue-100 p-6 rounded-lg shadow-md">
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

          {/* Reduction Strategies */}
          <section className="bg-white rounded-lg p-6 shadow-md">
            <h2 className="text-2xl font-semibold mb-4 text-center text-black">
              🌿 Reduction Strategies
            </h2>

            <div className="grid md:grid-cols-2 gap-6">
              {[
                {
                  icon: Lightbulb,
                  color: "text-yellow-500",
                  text: "Implement energy-efficient lighting across all facilities",
                },
                {
                  icon: Leaf,
                  color: "text-green-500",
                  text: "Increase use of renewable energy sources",
                },
                {
                  icon: Factory,
                  color: "text-gray-600",
                  text: "Optimize manufacturing processes to reduce waste",
                },
                {
                  icon: Home,
                  color: "text-blue-500",
                  text: "Encourage remote work to decrease commuting emissions",
                },
                {
                  icon: Car,
                  color: "text-red-500",
                  text: "Invest in electric vehicles for company fleet",
                },
              ].map((item, index) => (
                <div
                  key={index}
                  className="bg-gray-50 p-4 rounded-lg shadow-md flex items-center space-x-4"
                >
                  <item.icon className={`w-6 h-6 ${item.color}`} />
                  <p className="text-gray-700">{item.text}</p>
                </div>
              ))}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
