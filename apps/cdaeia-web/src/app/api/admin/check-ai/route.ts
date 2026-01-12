import { NextResponse } from 'next/server';

export async function GET() {
  const apiKey = process.env.ANTHROPIC_API_KEY;

  if (!apiKey) {
    return NextResponse.json({
      configured: false,
      message: 'Cle API non configuree'
    });
  }

  // Check if key looks valid (starts with sk-)
  if (!apiKey.startsWith('sk-')) {
    return NextResponse.json({
      configured: false,
      message: 'Format de cle invalide'
    });
  }

  return NextResponse.json({
    configured: true,
    message: 'API configuree et prete'
  });
}
