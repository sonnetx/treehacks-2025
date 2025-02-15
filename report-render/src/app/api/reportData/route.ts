import { NextResponse } from "next/server";

export async function GET() {
  try {
    // Fetch data from the hardcoded external API
    const response = await fetch("http://127.0.0.1:5000/api/data");
    const data = await response.json();

    return NextResponse.json({ message: "Data fetched successfully", data });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to fetch data", details: error },
      { status: 500 }
    );
  }
}
