"use client"

import type React from "react"

import { useEffect, useRef, useState } from "react"
import { ZoomIn, ZoomOut, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"

interface JsonViewerProps {
  data: any
}

interface TreeNode {
  id: string
  name: string
  x: number
  y: number
  children?: TreeNode[]
  data?: any
  width: number
  height: number
  parent?: TreeNode
  depth: number
}

interface Link {
  source: TreeNode
  target: TreeNode
}

const JsonViewer: React.FC<JsonViewerProps> = ({ data }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [scale, setScale] = useState(1)
  const [offset, setOffset] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [selectedNode, setSelectedNode] = useState<TreeNode | null>(null)
  const [tree, setTree] = useState<TreeNode | null>(null)
  const [links, setLinks] = useState<Link[]>([])

  // Process JSON data into a tree structure
  useEffect(() => {
    if (!data) return

    const nodeWidth = 150
    const nodeHeight = 40
    const horizontalSpacing = 80
    const verticalSpacing = 60

    // Convert JSON to tree structure
    const buildTree = (node: any, parentId = "", depth = 0): TreeNode => {
      const id = parentId ? `${parentId}-${node.name}` : node.name
      const treeNode: TreeNode = {
        id,
        name: node.name,
        x: 0, // Will be calculated later
        y: 0, // Will be calculated later
        width: nodeWidth,
        height: nodeHeight,
        depth,
        data: { ...node },
      }

      if (node.children && node.children.length > 0) {
        treeNode.children = node.children.map((child: any) => buildTree(child, id, depth + 1))

        // Set parent reference
        treeNode.children!.forEach((child) => {
          child.parent = treeNode
        })
      }

      return treeNode
    }

    // Calculate positions for the tree layout
    const calculatePositions = (node: TreeNode, x = 0, y = 0) => {
      node.x = x
      node.y = y

      if (node.children && node.children.length > 0) {
        const currentX = x + nodeWidth + horizontalSpacing
        const startY = y - ((node.children.length - 1) * (nodeHeight + verticalSpacing)) / 2

        node.children.forEach((child, index) => {
          const childY = startY + index * (nodeHeight + verticalSpacing)
          calculatePositions(child, currentX, childY)
        })
      }
    }

    // Build links between nodes
    const buildLinks = (node: TreeNode): Link[] => {
      let result: Link[] = []

      if (node.children && node.children.length > 0) {
        node.children.forEach((child) => {
          result.push({ source: node, target: child })
          result = [...result, ...buildLinks(child)]
        })
      }

      return result
    }

    const rootNode = buildTree(data)
    calculatePositions(rootNode)
    const treeLinks = buildLinks(rootNode)

    setTree(rootNode)
    setLinks(treeLinks)
  }, [data])

  // Draw the tree on canvas
  useEffect(() => {
    if (!canvasRef.current || !tree) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Set canvas size
    if (containerRef.current) {
      canvas.width = containerRef.current.clientWidth
      canvas.height = containerRef.current.clientHeight
    }

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Apply transformations
    ctx.save()
    ctx.translate(canvas.width / 2 + offset.x, canvas.height / 2 + offset.y)
    ctx.scale(scale, scale)

    // Draw links
    ctx.strokeStyle = "rgba(139, 92, 246, 0.5)"
    ctx.lineWidth = 2

    links.forEach((link) => {
      const sourceX = link.source.x + link.source.width
      const sourceY = link.source.y + link.source.height / 2
      const targetX = link.target.x
      const targetY = link.target.y + link.target.height / 2

      // Draw curved path
      ctx.beginPath()
      ctx.moveTo(sourceX, sourceY)

      const controlX = (sourceX + targetX) / 2

      ctx.bezierCurveTo(controlX, sourceY, controlX, targetY, targetX, targetY)

      ctx.stroke()
    })

    // Function to draw a node
    const drawNode = (node: TreeNode) => {
      // Node background
      ctx.fillStyle =
        node.id === selectedNode?.id
          ? "rgba(139, 92, 246, 0.8)"
          : node.children?.length
            ? "rgba(30, 41, 59, 0.9)"
            : "rgba(51, 65, 85, 0.9)"

      // Draw rounded rectangle
      const radius = 8
      ctx.beginPath()
      ctx.moveTo(node.x + radius, node.y)
      ctx.lineTo(node.x + node.width - radius, node.y)
      ctx.quadraticCurveTo(node.x + node.width, node.y, node.x + node.width, node.y + radius)
      ctx.lineTo(node.x + node.width, node.y + node.height - radius)
      ctx.quadraticCurveTo(
        node.x + node.width,
        node.y + node.height,
        node.x + node.width - radius,
        node.y + node.height,
      )
      ctx.lineTo(node.x + radius, node.y + node.height)
      ctx.quadraticCurveTo(node.x, node.y + node.height, node.x, node.y + node.height - radius)
      ctx.lineTo(node.x, node.y + radius)
      ctx.quadraticCurveTo(node.x, node.y, node.x + radius, node.y)
      ctx.closePath()
      ctx.fill()

      // Node border
      ctx.strokeStyle = node.id === selectedNode?.id ? "rgba(167, 139, 250, 1)" : "rgba(100, 116, 139, 0.6)"
      ctx.lineWidth = 2
      ctx.stroke()

      // Node text
      ctx.fillStyle = "#ffffff"
      ctx.font = "14px Inter, system-ui, sans-serif"
      ctx.textAlign = "center"
      ctx.textBaseline = "middle"

      // Truncate text if too long
      const maxTextWidth = node.width - 20
      let displayText = node.name
      if (ctx.measureText(displayText).width > maxTextWidth) {
        let truncated = ""
        for (let i = 0; i < displayText.length; i++) {
          const testText = displayText.substring(0, i) + "..."
          if (ctx.measureText(testText).width > maxTextWidth) {
            break
          }
          truncated = testText
        }
        displayText = truncated
      }

      ctx.fillText(displayText, node.x + node.width / 2, node.y + node.height / 2)
    }

    // Recursive function to draw the tree
    const drawTree = (node: TreeNode) => {
      drawNode(node)

      if (node.children) {
        node.children.forEach((child) => drawTree(child))
      }
    }

    // Draw the tree
    drawTree(tree)

    ctx.restore()
  }, [tree, links, scale, offset, selectedNode])

  // Handle canvas interactions
  useEffect(() => {
    if (!canvasRef.current || !tree) return

    const canvas = canvasRef.current

    const handleMouseDown = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top

      setIsDragging(true)
      setDragStart({ x, y })

      // Check if clicked on a node
      const canvasX = (x - canvas.width / 2 - offset.x) / scale
      const canvasY = (y - canvas.height / 2 - offset.y) / scale

      const findClickedNode = (node: TreeNode): TreeNode | null => {
        if (
          canvasX >= node.x &&
          canvasX <= node.x + node.width &&
          canvasY >= node.y &&
          canvasY <= node.y + node.height
        ) {
          return node
        }

        if (node.children) {
          for (const child of node.children) {
            const result = findClickedNode(child)
            if (result) return result
          }
        }

        return null
      }

      const clickedNode = findClickedNode(tree)
      setSelectedNode(clickedNode)
    }

    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return

      const rect = canvas.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top

      setOffset((prev) => ({
        x: prev.x + (x - dragStart.x),
        y: prev.y + (y - dragStart.y),
      }))

      setDragStart({ x, y })
    }

    const handleMouseUp = () => {
      setIsDragging(false)
    }

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault()

      const delta = -e.deltaY * 0.001
      const newScale = Math.min(Math.max(0.1, scale + delta), 2)

      setScale(newScale)
    }

    canvas.addEventListener("mousedown", handleMouseDown)
    canvas.addEventListener("mousemove", handleMouseMove)
    canvas.addEventListener("mouseup", handleMouseUp)
    canvas.addEventListener("mouseleave", handleMouseUp)
    canvas.addEventListener("wheel", handleWheel)

    return () => {
      canvas.removeEventListener("mousedown", handleMouseDown)
      canvas.removeEventListener("mousemove", handleMouseMove)
      canvas.removeEventListener("mouseup", handleMouseUp)
      canvas.removeEventListener("mouseleave", handleMouseUp)
      canvas.removeEventListener("wheel", handleWheel)
    }
  }, [tree, isDragging, dragStart, offset, scale])

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (!canvasRef.current || !containerRef.current) return

      canvasRef.current.width = containerRef.current.clientWidth
      canvasRef.current.height = containerRef.current.clientHeight
    }

    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  // Format JSON data for display
  const formatJsonData = (data: any) => {
    if (!data) return null

    // Handle different node types
    if (data.structure) {
      return (
        <div className="space-y-4">
          {data.structure.classes && (
            <div>
              <h3 className="text-sm font-medium text-slate-300 mb-2">Classes</h3>
              <div className="space-y-2">
                {data.structure.classes.map((cls: any, i: number) => (
                  <div key={i} className="bg-slate-800 p-3 rounded-md">
                    <p className="font-mono text-xs text-violet-400">{cls.name}</p>
                    {cls.methods && (
                      <div className="mt-2">
                        <p className="text-xs text-slate-400 mb-1">Methods:</p>
                        <ul className="list-disc list-inside">
                          {cls.methods.map((method: any, j: number) => (
                            <li key={j} className="text-xs text-slate-300">
                              {method.name}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {data.structure.other && (
            <div>
              <h3 className="text-sm font-medium text-slate-300 mb-2">Other</h3>
              <pre className="bg-slate-800 p-3 rounded-md font-mono text-xs text-slate-300 whitespace-pre-wrap">
                {data.structure.other}
              </pre>
            </div>
          )}
        </div>
      )
    }

    // Handle sink details
    if (data.sink_details && data.sink_details.length > 0) {
      return (
        <div>
          <h3 className="text-sm font-medium text-slate-300 mb-2">Sink Details</h3>
          <div className="space-y-3">
            {data.sink_details.map((sink: any, i: number) => (
              <div key={i} className="bg-slate-800 p-3 rounded-md">
                <div className="flex items-center mb-2">
                  <span className="px-2 py-1 bg-amber-900/50 text-amber-400 text-xs rounded-md font-medium">
                    {sink.ai_sink_label}
                  </span>
                </div>
                <p className="text-xs text-slate-300 mb-2">{sink.code_summary}</p>
                <pre className="bg-slate-900 p-2 rounded-md font-mono text-xs text-slate-300 whitespace-pre-wrap overflow-x-auto">
                  {sink.code_snippet}
                </pre>
                <div className="mt-2 text-xs text-slate-400">
                  Line: {sink.line_number}, Column: {sink.column_number}
                </div>
              </div>
            ))}
          </div>
        </div>
      )
    }

    // Handle vulnerabilities
    if (data.vulnerabilities && data.vulnerabilities.length > 0) {
      return (
        <div>
          <h3 className="text-sm font-medium text-slate-300 mb-2">Vulnerabilities</h3>
          <div className="space-y-3">
            {data.vulnerabilities.map((vuln: any, i: number) => (
              <div key={i} className="bg-slate-800 p-3 rounded-md">
                <div className="flex items-center mb-2">
                  <span
                    className={`px-2 py-1 ${
                      vuln.risk_level === "HIGH"
                        ? "bg-red-900/50 text-red-400"
                        : vuln.risk_level === "MEDIUM"
                          ? "bg-orange-900/50 text-orange-400"
                          : "bg-yellow-900/50 text-yellow-400"
                    } text-xs rounded-md font-medium`}
                  >
                    {vuln.risk_level} Risk
                  </span>
                </div>
                {vuln.code_snippet && (
                  <pre className="bg-slate-900 p-2 rounded-md font-mono text-xs text-slate-300 whitespace-pre-wrap overflow-x-auto mb-2">
                    {vuln.code_snippet}
                  </pre>
                )}
                <div className="text-xs text-slate-400">Line: {vuln.line_number}</div>
                {vuln.ref_link && (
                  <a
                    href={vuln.ref_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-violet-400 hover:underline mt-1 inline-block"
                  >
                    Reference Documentation
                  </a>
                )}
                {vuln.message_to_fix && (
                  <div className="mt-2">
                    <p className="text-xs text-slate-400">Fix:</p>
                    <code className="text-xs text-green-400 font-mono">{vuln.message_to_fix}</code>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )
    }

    // Default display for other data
    return (
      <pre className="bg-slate-800 p-3 rounded-md font-mono text-xs text-slate-300 whitespace-pre-wrap">
        {JSON.stringify(data, null, 2)}
      </pre>
    )
  }

  return (
    <div className="relative h-full" ref={containerRef}>
      <canvas ref={canvasRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

      <div className="absolute bottom-4 right-4 flex gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setScale((prev) => Math.min(prev + 0.1, 2))}
          className="bg-slate-800 border-slate-700 hover:bg-slate-700 text-white"
        >
          <ZoomIn className="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setScale((prev) => Math.max(prev - 0.1, 0.1))}
          className="bg-slate-800 border-slate-700 hover:bg-slate-700 text-white"
        >
          <ZoomOut className="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            setScale(1)
            setOffset({ x: 0, y: 0 })
          }}
          className="bg-slate-800 border-slate-700 hover:bg-slate-700 text-white"
        >
          Reset
        </Button>
      </div>

      {selectedNode && (
        <div className="absolute top-4 right-4 w-80">
          <Card className="bg-slate-800 border-slate-700 shadow-xl">
            <CardHeader className="pb-2 flex flex-row items-center justify-between">
              <CardTitle className="text-sm font-medium text-white">{selectedNode.name}</CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedNode(null)}
                className="h-8 w-8 p-0 text-slate-400 hover:text-white"
              >
                <X className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[300px] pr-4">{formatJsonData(selectedNode.data)}</ScrollArea>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

export default JsonViewer

