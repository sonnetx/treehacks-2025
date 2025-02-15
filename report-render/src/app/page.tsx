"use client";

import { BarChart, Lightbulb, Factory, Car } from "lucide-react";
import { useEffect, useState } from "react";

export default function CarbonEmissionsReport() {
  const currentDate = new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("/api/reportData") // Calls the Next.js API
      .then((res) => res.json())
      .then((data) => {
        setMessage(data.message); // ✅ Set state
        console.log(data.message);
        console.log(data.data); // ✅ Log message properly
      })
      .catch((error) => console.error("Error fetching data:", error));
  }, []);

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
            <p className="text-gray-600">
              This report provides an overview of our organization's carbon
              emissions for the past year. We've made significant progress in
              reducing our carbon footprint, but there's still work to be done.
              Our total emissions have decreased by 15% compared to the previous
              year.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4 text-black">
              Emissions Overview
            </h2>
            <div>
              <div>
                <div className="text-black">Total Emissions</div>
              </div>
              <div>
                <div className="h-[200px] flex items-center justify-center bg-gray-100 rounded-md">
                  <div className="w-16 h-16 text-gray-400 text-black" />
                  <span className="sr-only">
                    Placeholder for emissions chart
                  </span>
                </div>
                <p className="text-sm text-gray-500 mt-2 text-center">
                  Chart: Annual Carbon Emissions (metric tons CO2e)
                </p>
              </div>
            </div>
          </section>

          <section>
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
