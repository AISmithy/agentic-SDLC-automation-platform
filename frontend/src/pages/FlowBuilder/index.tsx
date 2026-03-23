/**
 * Flow Builder — canvas-based drag-and-drop workflow designer.
 * Uses ReactFlow for the visual editing surface.
 */

import { useState, useCallback } from "react";
import ReactFlow, {
  addEdge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Connection,
  Edge,
  Node,
} from "reactflow";
import "reactflow/dist/style.css";
import { Save, Play, Plus, ChevronRight } from "lucide-react";
import clsx from "clsx";

const NODE_TYPES = [
  { type: "trigger", label: "Trigger", color: "bg-blue-100 border-blue-400 text-blue-800" },
  { type: "agent", label: "Agent Task", color: "bg-purple-100 border-purple-400 text-purple-800" },
  { type: "mcp_tool", label: "MCP Tool", color: "bg-indigo-100 border-indigo-400 text-indigo-800" },
  { type: "approval", label: "Approval Gate", color: "bg-amber-100 border-amber-400 text-amber-800" },
  { type: "condition", label: "Condition", color: "bg-yellow-100 border-yellow-400 text-yellow-800" },
  { type: "pr_action", label: "PR Action", color: "bg-green-100 border-green-400 text-green-800" },
  { type: "deploy_action", label: "Deploy Action", color: "bg-teal-100 border-teal-400 text-teal-800" },
  { type: "notification", label: "Notification", color: "bg-gray-100 border-gray-400 text-gray-700" },
];

const COLOR_MAP: Record<string, string> = Object.fromEntries(
  NODE_TYPES.map((n) => [n.type, n.color])
);

const INITIAL_NODES: Node[] = [
  {
    id: "trigger-1",
    type: "default",
    position: { x: 250, y: 50 },
    data: { label: "Story Selected" },
    style: { background: "#dbeafe", border: "1.5px solid #60a5fa", borderRadius: "8px" },
  },
  {
    id: "agent-1",
    type: "default",
    position: { x: 250, y: 160 },
    data: { label: "Story Analysis Agent" },
    style: { background: "#ede9fe", border: "1.5px solid #a78bfa", borderRadius: "8px" },
  },
  {
    id: "approval-1",
    type: "default",
    position: { x: 250, y: 270 },
    data: { label: "Plan Approval" },
    style: { background: "#fef3c7", border: "1.5px solid #fbbf24", borderRadius: "8px" },
  },
  {
    id: "mcp-1",
    type: "default",
    position: { x: 250, y: 380 },
    data: { label: "Create Branch (MCP)" },
    style: { background: "#e0e7ff", border: "1.5px solid #818cf8", borderRadius: "8px" },
  },
  {
    id: "agent-2",
    type: "default",
    position: { x: 250, y: 490 },
    data: { label: "Code Proposal Agent" },
    style: { background: "#ede9fe", border: "1.5px solid #a78bfa", borderRadius: "8px" },
  },
  {
    id: "pr-1",
    type: "default",
    position: { x: 250, y: 600 },
    data: { label: "Create PR (MCP)" },
    style: { background: "#dcfce7", border: "1.5px solid #4ade80", borderRadius: "8px" },
  },
];

const INITIAL_EDGES: Edge[] = [
  { id: "e1-2", source: "trigger-1", target: "agent-1", animated: true },
  { id: "e2-3", source: "agent-1", target: "approval-1" },
  { id: "e3-4", source: "approval-1", target: "mcp-1" },
  { id: "e4-5", source: "mcp-1", target: "agent-2" },
  { id: "e5-6", source: "agent-2", target: "pr-1" },
];

let nodeCounter = 10;

export default function FlowBuilder() {
  const [nodes, setNodes, onNodesChange] = useNodesState(INITIAL_NODES);
  const [edges, setEdges, onEdgesChange] = useEdgesState(INITIAL_EDGES);
  const [selectedNodeType, setSelectedNodeType] = useState("agent");
  const [saved, setSaved] = useState(false);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge({ ...params, animated: false }, eds)),
    [setEdges]
  );

  const addNode = useCallback(() => {
    const info = NODE_TYPES.find((n) => n.type === selectedNodeType);
    const id = `${selectedNodeType}-${++nodeCounter}`;
    setNodes((nds) => [
      ...nds,
      {
        id,
        type: "default",
        position: { x: 200 + Math.random() * 100, y: 100 + nds.length * 110 },
        data: { label: info?.label ?? selectedNodeType },
        style: {
          background: "#f3f4f6",
          border: "1.5px solid #9ca3af",
          borderRadius: "8px",
        },
      },
    ]);
  }, [selectedNodeType, setNodes]);

  const handleSave = () => {
    // TODO: serialize and POST to /api/v1/workflows/templates/
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="flex h-full flex-col">
      {/* Toolbar */}
      <div className="flex items-center gap-3 border-b bg-white px-6 py-3">
        <h1 className="font-semibold text-gray-900">Flow Builder</h1>
        <ChevronRight className="h-4 w-4 text-gray-400" />
        <span className="text-sm text-gray-500">Untitled Workflow</span>

        <div className="ml-auto flex items-center gap-2">
          {/* Node type picker */}
          <select
            value={selectedNodeType}
            onChange={(e) => setSelectedNodeType(e.target.value)}
            className="rounded-md border px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            {NODE_TYPES.map((n) => (
              <option key={n.type} value={n.type}>{n.label}</option>
            ))}
          </select>
          <button onClick={addNode} className="btn-secondary text-xs gap-1">
            <Plus className="h-3.5 w-3.5" />
            Add Node
          </button>
          <button onClick={handleSave} className="btn-primary text-xs">
            <Save className="h-3.5 w-3.5" />
            {saved ? "Saved!" : "Save"}
          </button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Canvas */}
        <div className="flex-1">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            fitView
          >
            <Background />
            <Controls />
            <MiniMap nodeStrokeWidth={3} />
          </ReactFlow>
        </div>

        {/* Right panel — node palette */}
        <aside className="w-56 shrink-0 border-l bg-white overflow-y-auto p-4">
          <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-500">Node Types</p>
          <div className="space-y-2">
            {NODE_TYPES.map((n) => (
              <button
                key={n.type}
                onClick={() => setSelectedNodeType(n.type)}
                className={clsx(
                  "w-full rounded-md border px-3 py-2 text-left text-xs font-medium transition-all",
                  n.color,
                  selectedNodeType === n.type ? "ring-2 ring-primary-500" : ""
                )}
              >
                {n.label}
              </button>
            ))}
          </div>

          <div className="mt-6 rounded-md bg-blue-50 p-3">
            <p className="text-xs font-medium text-blue-800">Tip</p>
            <p className="mt-1 text-xs text-blue-600">
              Connect nodes by dragging from one handle to another. Approval nodes gate high-risk actions.
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}
