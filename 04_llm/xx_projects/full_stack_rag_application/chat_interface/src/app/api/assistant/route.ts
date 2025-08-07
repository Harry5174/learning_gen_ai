import { NextRequest, NextResponse } from "next/server";
import axios from "axios";

const baseUrl = "http://127.0.0.1:8000";


interface ChatRequest {
    query: string;
}

export async function POST(request: NextRequest) {
  try {
    const url = `${baseUrl}/chat`;

    const requestBody = await request.json();
    const query: string = requestBody.query;

    if (!requestBody.query || typeof requestBody.query !== "string") {
        throw new Error("prompt field is required and must be a string");
    }
    const req :ChatRequest = {
        query: query,
    }

    console.log({ Nextrequest: req });

    const response = await axios.post(url, { query });

    return NextResponse.json(response.data);

  } catch (error: any) {
    console.error("Error handling POST request: ", error);
    return NextResponse.json(
      { error: `Error handling POST request: ${error.message}` },
      { status: 500 }
    );
  }
}
