import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const body = await request.json()
  // TODO: Forward approval to backend orchestrator
  return NextResponse.json({ success: true, message: "Approval sent to agent" })
}
