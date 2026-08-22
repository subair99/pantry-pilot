export default function ApprovalPage({ params }: { params: { id: string } }) {
  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Decision Required</h1>
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <p className="mb-4">Agent ID: {params.id}</p>
        <p className="text-gray-600 mb-6">The agent has drafted an action. Please review and approve.</p>
        <div className="flex gap-4">
          <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">Approve</button>
          <button className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">Reject</button>
        </div>
      </div>
    </div>
  )
}
