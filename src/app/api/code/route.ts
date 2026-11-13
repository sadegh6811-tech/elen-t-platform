import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { prompt } = await request.json();
    const apiKey = process.env.GROQ_API_KEY;

    if (!apiKey) {
      return NextResponse.json({ success: false, error: "GROQ_API_KEY not configured" }, { status: 500 });
    }

    const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "openai/gpt-oss-120b",
        messages: [
          { role: "system", content: "You are an expert Python developer. Write clean, well-commented Python code. Only return the code, no explanations." },
          { role: "user", content: prompt }
        ],
        temperature: 0.3,
        max_tokens: 2000
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json({ success: false, error: JSON.stringify(errorData) }, { status: response.status });
    }

    const data = await response.json();
    const code = data.choices?.[0]?.message?.content || "No code generated.";

    return NextResponse.json({ success: true, code });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
