"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Search, ChevronLeft, ChevronRight } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"

interface CsvViewerProps {
  data: string
}

interface CsvRow {
  [key: string]: string
}

const CsvViewer: React.FC<CsvViewerProps> = ({ data }) => {
  const [parsedData, setParsedData] = useState<CsvRow[]>([])
  const [headers, setHeaders] = useState<string[]>([])
  const [currentPage, setCurrentPage] = useState(1)
  const [searchTerm, setSearchTerm] = useState("")
  const [filteredData, setFilteredData] = useState<CsvRow[]>([])
  const rowsPerPage = 10

  // Parse CSV data
  useEffect(() => {
    if (!data) return

    // Split by rows and handle quoted values properly
    const parseCSV = (csvText: string) => {
      const rows: string[][] = []
      let currentRow: string[] = []
      let currentValue = ""
      let insideQuotes = false

      for (let i = 0; i < csvText.length; i++) {
        const char = csvText[i]
        const nextChar = csvText[i + 1]

        if (char === '"') {
          if (insideQuotes && nextChar === '"') {
            // Handle escaped quotes
            currentValue += '"'
            i++ // Skip the next quote
          } else {
            // Toggle quote state
            insideQuotes = !insideQuotes
          }
        } else if (char === "," && !insideQuotes) {
          // End of field
          currentRow.push(currentValue)
          currentValue = ""
        } else if ((char === "\n" || (char === "\r" && nextChar === "\n")) && !insideQuotes) {
          // End of row
          currentRow.push(currentValue)
          rows.push(currentRow)
          currentRow = []
          currentValue = ""

          if (char === "\r") {
            i++ // Skip the \n in \r\n
          }
        } else {
          currentValue += char
        }
      }

      // Add the last row if there's any data
      if (currentValue || currentRow.length > 0) {
        currentRow.push(currentValue)
        rows.push(currentRow)
      }

      return rows
    }

    const rows = parseCSV(data)

    if (rows.length > 0) {
      const headerRow = rows[0]
      setHeaders(headerRow)

      const dataRows = rows.slice(1).map((row) => {
        const rowData: CsvRow = {}
        headerRow.forEach((header, index) => {
          rowData[header] = row[index] || ""
        })
        return rowData
      })

      setParsedData(dataRows)
      setFilteredData(dataRows)
    }
  }, [data])

  // Filter data based on search term
  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredData(parsedData)
      setCurrentPage(1)
      return
    }

    const term = searchTerm.toLowerCase()
    const filtered = parsedData.filter((row) => Object.values(row).some((value) => value.toLowerCase().includes(term)))

    setFilteredData(filtered)
    setCurrentPage(1)
  }, [searchTerm, parsedData])

  // Calculate pagination
  const totalPages = Math.ceil(filteredData.length / rowsPerPage)
  const startIndex = (currentPage - 1) * rowsPerPage
  const endIndex = startIndex + rowsPerPage
  const currentData = filteredData.slice(startIndex, endIndex)

  // Format code snippets for display
  const formatCodeSnippet = (content: string) => {
    if (!content) return null

    // Check if this is a sink or vulnerability section
    if (content.includes("<SINK>") || content.includes("<VULNERABILITIES>")) {
      const sections = []

      // Parse sink sections
      if (content.includes("<SINK>")) {
        const sinkMatches = content.match(/<SINK>([\s\S]*?)<\/SINK>/g)
        if (sinkMatches) {
          sinkMatches.forEach((match, index) => {
            const sinkContent = match.replace(/<SINK>|<\/SINK>/g, "").trim()
            const lines = sinkContent.split("\n")

            // First line is usually the sink label
            const label = lines[0]
            // Second line is usually the description
            const description = lines[1]
            // The rest is the code snippet
            const code = lines.slice(2).join("\n").trim()

            sections.push(
              <div key={`sink-${index}`} className="mb-4 bg-slate-800 rounded-md p-3">
                <div className="px-2 py-1 bg-amber-900/50 text-amber-400 text-xs rounded-md font-medium inline-block mb-2">
                  {label}
                </div>
                <p className="text-xs text-slate-300 mb-2">{description}</p>
                <pre className="bg-slate-900 p-2 rounded-md font-mono text-xs text-slate-300 whitespace-pre-wrap overflow-x-auto">
                  {code}
                </pre>
              </div>,
            )
          })
        }
      }

      // Parse vulnerability sections
      if (content.includes("<VULNERABILITIES>")) {
        const vulnMatches = content.match(/<VULNERABILITIES>([\s\S]*?)<\/VULNERABILITIES>/g)
        if (vulnMatches) {
          vulnMatches.forEach((match, index) => {
            const vulnContent = match.replace(/<VULNERABILITIES>|<\/VULNERABILITIES>/g, "").trim()
            const lines = vulnContent.split("\n").filter((line) => line.trim())

            if (lines.length >= 1) {
              // First line is usually the risk level
              const riskLevel = lines[0].trim()
              // Second line is usually the reference link
              const refLink = lines.length > 1 ? lines[1].trim() : ""
              // Third line is usually the fix message
              const fixMessage = lines.length > 2 ? lines[2].trim() : ""

              sections.push(
                <div key={`vuln-${index}`} className="mb-4 bg-slate-800 rounded-md p-3">
                  <div
                    className={`px-2 py-1 ${
                      riskLevel.includes("HIGH")
                        ? "bg-red-900/50 text-red-400"
                        : riskLevel.includes("MEDIUM")
                          ? "bg-orange-900/50 text-orange-400"
                          : "bg-yellow-900/50 text-yellow-400"
                    } text-xs rounded-md font-medium inline-block mb-2`}
                  >
                    {riskLevel}
                  </div>
                  {refLink && (
                    <a
                      href={refLink}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-violet-400 hover:underline block mb-2"
                    >
                      {refLink}
                    </a>
                  )}
                  {fixMessage && (
                    <div className="mt-2">
                      <p className="text-xs text-slate-400">Fix:</p>
                      <code className="text-xs text-green-400 font-mono">{fixMessage}</code>
                    </div>
                  )}
                </div>,
              )
            }
          })
        }
      }

      return <div>{sections}</div>
    }

    // Default code formatting
    return (
      <pre className="bg-slate-800 p-2 rounded-md font-mono text-xs text-slate-300 whitespace-pre-wrap overflow-x-auto">
        {content}
      </pre>
    )
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-slate-800 bg-slate-900">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 h-4 w-4" />
          <Input
            type="text"
            placeholder="Search table..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 bg-slate-800 border-slate-700 text-white placeholder:text-slate-400"
          />
        </div>
      </div>

      <ScrollArea className="flex-grow">
        <div className="min-w-max">
          <table className="w-full border-collapse">
            <thead className="bg-slate-900 sticky top-0 z-10">
              <tr>
                {headers.map((header, index) => (
                  <th
                    key={index}
                    className="px-4 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider border-b border-slate-800"
                  >
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {currentData.map((row, rowIndex) => (
                <tr key={rowIndex} className="hover:bg-slate-800/50 border-b border-slate-800 last:border-0">
                  {headers.map((header, colIndex) => (
                    <td key={colIndex} className="px-4 py-4 text-sm text-slate-300 align-top">
                      {header === "Code Snippet" || header === "Sinks" || header === "Vulnerabilities"
                        ? formatCodeSnippet(row[header])
                        : row[header]}
                    </td>
                  ))}
                </tr>
              ))}

              {currentData.length === 0 && (
                <tr>
                  <td colSpan={headers.length} className="px-4 py-8 text-center text-sm text-slate-400">
                    {searchTerm ? "No results found" : "No data available"}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </ScrollArea>

      {totalPages > 1 && (
        <div className="p-4 border-t border-slate-800 bg-slate-900 flex items-center justify-between">
          <div className="text-sm text-slate-400">
            Showing {startIndex + 1}-{Math.min(endIndex, filteredData.length)} of {filteredData.length} results
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="h-8 w-8 p-0 bg-slate-800 border-slate-700 hover:bg-slate-700 text-white"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm text-slate-300">
              {currentPage} / {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="h-8 w-8 p-0 bg-slate-800 border-slate-700 hover:bg-slate-700 text-white"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

export default CsvViewer

