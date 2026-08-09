import { useState, useEffect, useRef } from 'react';
import apiClient from '../api/client';
import toast from 'react-hot-toast';
import { 
  CalendarIcon, 
  ArrowPathIcon, 
  DocumentArrowDownIcon,
  DocumentArrowUpIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronDownIcon
} from '@heroicons/react/24/outline';
import * as XLSX from 'xlsx';

interface TimesheetEntry {
  id: number;
  task_id: number;
  task_title: string;
  project_name?: string;
  project_id?: number;
  user_id?: number;
  user_name?: string;
  user_email?: string;
  date: string;
  hours: number;
  description?: string;
  created_at: string;
}

interface DailySummary {
  date: string;
  total_hours: number;
  entries: TimesheetEntry[];
}

const TimesheetReport = () => {
  const [entries, setEntries] = useState<TimesheetEntry[]>([]);
  const [dailySummary, setDailySummary] = useState<DailySummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalHours, setTotalHours] = useState(0);
  const [viewMode, setViewMode] = useState<'week' | 'month'>('week');
  const [currentDate, setCurrentDate] = useState(new Date());
  const [showExportMenu, setShowExportMenu] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchTimesheets();
  }, [viewMode, currentDate]);

  /**
   * Format a Date object to YYYY-MM-DD string
   */
  const formatDateToYYYYMMDD = (date: Date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  /**
   * Get the start and end dates for the current month
   */
  const getMonthRange = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    
    const start = new Date(year, month, 1);
    const startDate = formatDateToYYYYMMDD(start);
    
    const end = new Date(year, month + 1, 0);
    const endDate = formatDateToYYYYMMDD(end);
    
    return { startDate, endDate };
  };

  /**
   * Get the start and end dates for the current week (Monday to Sunday)
   */
  const getWeekRange = (date: Date) => {
    const start = new Date(date);
    start.setDate(date.getDate() - date.getDay());
    const startDate = formatDateToYYYYMMDD(start);
    
    const end = new Date(start);
    end.setDate(start.getDate() + 6);
    const endDate = formatDateToYYYYMMDD(end);
    
    return { startDate, endDate };
  };

  /**
   * Fetch timesheet entries for the selected date range
   */
  const fetchTimesheets = async () => {
    setLoading(true);
    try {
      let startDate = '';
      let endDate = '';
      
      if (viewMode === 'week') {
        const range = getWeekRange(currentDate);
        startDate = range.startDate;
        endDate = range.endDate;
      } else {
        const range = getMonthRange(currentDate);
        startDate = range.startDate;
        endDate = range.endDate;
      }

      const res = await apiClient.get('/timesheets/my', {
        params: { start_date: startDate, end_date: endDate }
      });
      
      // Enrich entries with project and user details
      const entriesWithData = await Promise.all(
        res.data.map(async (entry: any) => {
          try {
            const taskRes = await apiClient.get(`/tasks/${entry.task_id}`);
            const taskData = taskRes.data;
            
            const projectRes = await apiClient.get(`/projects/${taskData.project_id}`);
            const projectData = projectRes.data;
            
            let userEmail = 'unknown@email.com';
            let userName = 'Unknown';
            try {
              const userRes = await apiClient.get(`/users/${entry.user_id}`);
              userEmail = userRes.data.email;
              userName = userRes.data.name;
            } catch {
              // User fetch failed, use defaults
            }
            
            return {
              ...entry,
              project_name: projectData.name,
              project_id: projectData.id,
              user_email: userEmail,
              user_name: userName
            };
          } catch {
            return { 
              ...entry, 
              project_name: 'Unknown', 
              project_id: null,
              user_email: 'unknown@email.com',
              user_name: 'Unknown'
            };
          }
        })
      );
      
      setEntries(entriesWithData);
      processData(entriesWithData);
    } catch (error) {
      toast.error('Failed to load timesheet report');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Process entries into daily summaries
   */
  const processData = (data: TimesheetEntry[]) => {
    const dailyMap: { [key: string]: TimesheetEntry[] } = {};
    let total = 0;

    data.forEach(entry => {
      const dateKey = entry.date;
      if (!dailyMap[dateKey]) {
        dailyMap[dateKey] = [];
      }
      dailyMap[dateKey].push(entry);
      total += entry.hours;
    });

    const summary: DailySummary[] = Object.keys(dailyMap)
      .sort((a, b) => new Date(b).getTime() - new Date(a).getTime())
      .map(date => ({
        date,
        total_hours: dailyMap[date].reduce((sum, e) => sum + e.hours, 0),
        entries: dailyMap[date]
      }));

    setDailySummary(summary);
    setTotalHours(total);
  };

  /**
   * Export data to Excel (.xlsx) format
   */
  const exportToExcel = () => {
    if (entries.length === 0) {
      toast.error('No data to export');
      return;
    }

    const exportData = entries.map(entry => ({
      'User ID': entry.user_id || 'N/A',
      'User Email': entry.user_email || 'unknown@email.com',
      'User Name': entry.user_name || 'Unknown',
      'Project ID': entry.project_id || 'N/A',
      'Project Name': entry.project_name || 'Unknown',
      'Task ID': entry.task_id,
      'Task Name': entry.task_title,
      'Date': entry.date,
      'Hours': entry.hours,
      'Description': entry.description || '',
      'Created At': entry.created_at
    }));

    const ws = XLSX.utils.json_to_sheet(exportData);
    
    const colWidths = [
      { wch: 10 }, // User ID
      { wch: 25 }, // User Email
      { wch: 20 }, // User Name
      { wch: 12 }, // Project ID
      { wch: 20 }, // Project Name
      { wch: 10 }, // Task ID
      { wch: 30 }, // Task Name
      { wch: 12 }, // Date
      { wch: 10 }, // Hours
      { wch: 30 }, // Description
      { wch: 20 }, // Created At
    ];
    ws['!cols'] = colWidths;

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Timesheet');
    
    XLSX.writeFile(wb, `timesheet_${new Date().toISOString().split('T')[0]}.xlsx`);
    toast.success('Exported successfully!');
    setShowExportMenu(false);
  };

  /**
   * Export data to CSV format
   */
  const exportToCSV = () => {
    if (entries.length === 0) {
      toast.error('No data to export');
      return;
    }

    let csv = 'User ID,User Email,User Name,Project ID,Project Name,Task ID,Task Name,Date,Hours,Description,Created At\n';
    
    entries.forEach(entry => {
      csv += `"${entry.user_id || 'N/A'}","${entry.user_email || 'unknown@email.com'}","${entry.user_name || 'Unknown'}","${entry.project_id || 'N/A'}","${entry.project_name || 'Unknown'}",${entry.task_id},"${entry.task_title}",${entry.date},${entry.hours},"${entry.description || ''}","${entry.created_at}"\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `timesheet_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    toast.success('Exported successfully!');
    setShowExportMenu(false);
  };

  /**
   * Import timesheet entries from Excel or CSV file
   * Supports multiple date formats and automatic field mapping
   */
  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (event) => {
      try {
        const data = event.target?.result;
        let importedEntries: any[] = [];

        // Parse file based on extension
        if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
          const workbook = XLSX.read(data, { type: 'array' });
          const sheet = workbook.Sheets[workbook.SheetNames[0]];
          importedEntries = XLSX.utils.sheet_to_json(sheet);
        } else if (file.name.endsWith('.csv')) {
          const text = data as string;
          const lines = text.split('\n');
          const headers = lines[0].split(',');
          importedEntries = lines.slice(1).filter(line => line.trim()).map(line => {
            const values = line.split(',');
            const entry: any = {};
            headers.forEach((h, i) => {
              entry[h.trim()] = values[i]?.trim();
            });
            return entry;
          });
        }

        if (importedEntries.length === 0) {
          toast.error('No valid data found in file');
          return;
        }

        let successCount = 0;
        let errorCount = 0;
        const errors: string[] = [];
        let missingFieldsCount = 0;

        // Process each imported entry
        for (const [index, entry] of importedEntries.entries()) {
          try {
            const rowNumber = index + 2;

            const missingFields: string[] = [];

            const userId = entry['User ID'];
            const userEmail = entry['User Email']?.trim();
            const userName = entry['User Name']?.trim();

            const projectId = entry['Project ID'];
            const projectName = entry['Project Name']?.trim();

            const taskId = entry['Task ID'];
            const taskName = entry['Task Name']?.trim();

            // Validate required fields
            if (!userId && !userEmail && !userName) {
              missingFields.push('User ID / User Email / User Name');
            }

            if (!projectId && !projectName) {
              missingFields.push('Project ID / Project Name');
            }

            if (!taskId && !taskName) {
              missingFields.push('Task ID / Task Name');
            }

            if (missingFields.length > 0) {
              const errorMsg = `Row ${rowNumber}: Missing fields: ${missingFields.join(', ')}`;
              errors.push(errorMsg);
              missingFieldsCount++;
              errorCount++;
              continue;
            }

            // Find project by ID or name
            let project = null;

            if (projectId && projectId !== 'N/A') {
              try {
                const projectRes = await apiClient.get(`/projects/${projectId}`);
                project = projectRes.data;
              } catch {
                // Project not found by ID, try by name
              }
            }

            if (!project && projectName) {
              const projectsRes = await apiClient.get('/projects/search', {
                params: { q: projectName }
              });
              if (projectsRes.data.length > 0) {
                project = projectsRes.data[0];
              }
            }

            if (!project) {
              errors.push(`Row ${rowNumber}: Project "${projectName || projectId}" not found`);
              errorCount++;
              continue;
            }

            // Find task by ID or name within the project
            let task = null;

            if (taskId) {
              try {
                const taskRes = await apiClient.get(`/tasks/${taskId}`);
                task = taskRes.data;
              } catch {
                // Task not found by ID, try by name
              }
            }

            if (!task && taskName) {
              const params: any = { q: taskName, project_id: project.id };
              const tasksRes = await apiClient.get('/tasks/search', { params });
              if (tasksRes.data.length > 0) {
                task = tasksRes.data[0];
              }
            }

            if (!task) {
              errors.push(`Row ${rowNumber}: Task "${taskName || taskId}" not found in project "${project.name}"`);
              errorCount++;
              continue;
            }

            // Find target user by ID, email, or name
            let targetUserId = null;

            if (userId && userId !== 'N/A') {
              try {
                const userRes = await apiClient.get(`/users/${Number(userId)}`);
                if (userRes.data) {
                  targetUserId = userRes.data.id;
                }
              } catch {
                // User not found
              }
            }

            if (!targetUserId && userEmail && userEmail !== 'unknown@email.com') {
              try {
                const usersRes = await apiClient.get('/users');
                const foundUser = usersRes.data.find((u: any) =>
                  u.email?.toLowerCase() === userEmail?.toLowerCase()
                );
                if (foundUser) {
                  targetUserId = foundUser.id;
                }
              } catch {
                // User not found
              }
            }

            if (!targetUserId && userName && userName !== 'Unknown') {
              try {
                const usersRes = await apiClient.get('/users');
                const foundUser = usersRes.data.find((u: any) =>
                  u.name?.toLowerCase() === userName?.toLowerCase()
                );
                if (!foundUser) {
                  const foundUserPartial = usersRes.data.find((u: any) =>
                    u.name?.toLowerCase().includes(userName?.toLowerCase())
                  );
                  if (foundUserPartial) {
                    targetUserId = foundUserPartial.id;
                  }
                } else {
                  targetUserId = foundUser.id;
                }
              } catch {
                // User not found
              }
            }

            // Fallback to current user if no user found
            if (!targetUserId) {
              const meRes = await apiClient.get('/auth/users/me');
              targetUserId = meRes.data.id;
            }

            // Parse date with multiple format support
            let dateValue = entry['Date'] || entry['date'];
            let formattedDate = new Date().toISOString().split('T')[0];

            if (dateValue) {
              let parsedDate = null;

              // Handle Excel numeric date format
              if (typeof dateValue === 'number') {
                const excelDate = new Date((dateValue - 25569) * 86400 * 1000);
                if (!isNaN(excelDate.getTime())) {
                  parsedDate = excelDate;
                }
              } else {
                const dateStr = String(dateValue).trim();

                // Try multiple date formats
                const formats = [
                  /^(\d{4})-(\d{2})-(\d{2})/,
                  /^(\d{2})\/(\d{2})\/(\d{4})/,
                  /^(\d{2})-(\d{2})-(\d{4})/,
                  /^(\d{4})\/(\d{2})\/(\d{2})/,
                ];

                for (const format of formats) {
                  const match = dateStr.match(format);
                  if (match) {
                    const year = parseInt(match[1]);
                    const month = parseInt(match[2]) - 1;
                    const day = parseInt(match[3]);
                    const d = new Date(year, month, day);
                    if (!isNaN(d.getTime())) {
                      parsedDate = d;
                      break;
                    }
                  }
                }

                // Fallback to native Date parsing
                if (!parsedDate) {
                  const d = new Date(dateStr);
                  if (!isNaN(d.getTime())) {
                    parsedDate = d;
                  }
                }
              }

              if (parsedDate) {
                formattedDate = parsedDate.toISOString().split('T')[0];
              }
            }

            // Parse hours
            let hours = parseFloat(entry['Hours'] || entry['hours'] || 0);
            if (isNaN(hours) || hours <= 0) {
              errors.push(`Row ${rowNumber}: Invalid hours "${entry['Hours']}"`);
              errorCount++;
              continue;
            }

            const description = entry['Description'] || entry['description'] || '';

            // Create the timesheet entry
            await apiClient.post('/timesheets', {
              task_id: task.id,
              user_id: targetUserId,
              date: formattedDate,
              hours: hours,
              description: description
            });

            successCount++;
          } catch (err) {
            errors.push(`Row ${index + 2}: ${err instanceof Error ? err.message : 'Unknown error'}`);
            errorCount++;
          }
        }

        // Display import results
        let message = '';
        if (successCount > 0 && errorCount === 0) {
          message = `✅ Imported ${successCount} entries successfully!`;
          toast.success(message);
        } else if (successCount > 0 && errorCount > 0) {
          message = `⚠️ Imported ${successCount} entries, ${errorCount} failed.\n\n${errors.slice(0, 5).join('\n')}${errors.length > 5 ? `\n... and ${errors.length - 5} more errors` : ''}`;
          toast.error(message, { duration: 8000 });
        } else {
          message = `❌ Failed to import ${errorCount} entries.\n\n${errors.slice(0, 5).join('\n')}${errors.length > 5 ? `\n... and ${errors.length - 5} more errors` : ''}`;
          toast.error(message, { duration: 8000 });
        }

        // Refresh the timesheet data
        fetchTimesheets();
      } catch (error) {
        toast.error('Failed to import file');
      }
    };

    if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
      reader.readAsArrayBuffer(file);
    } else {
      reader.readAsText(file);
    }

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  /**
   * Get the display range string based on view mode
   */
  const getDisplayRange = () => {
    if (viewMode === 'week') {
      const { startDate, endDate } = getWeekRange(currentDate);
      return `${new Date(startDate).toLocaleDateString()} - ${new Date(endDate).toLocaleDateString()}`;
    } else {
      const { startDate, endDate } = getMonthRange(currentDate);
      return `${new Date(startDate).toLocaleDateString()} - ${new Date(endDate).toLocaleDateString()}`;
    }
  };

  /**
   * Navigate to previous week/month
   */
  const navigatePrevious = () => {
    const newDate = new Date(currentDate);
    if (viewMode === 'week') {
      newDate.setDate(currentDate.getDate() - 7);
    } else {
      newDate.setMonth(currentDate.getMonth() - 1);
    }
    setCurrentDate(newDate);
  };

  /**
   * Navigate to next week/month
   */
  const navigateNext = () => {
    const newDate = new Date(currentDate);
    if (viewMode === 'week') {
      newDate.setDate(currentDate.getDate() + 7);
    } else {
      newDate.setMonth(currentDate.getMonth() + 1);
    }
    setCurrentDate(newDate);
  };

  /**
   * Jump to today
   */
  const goToToday = () => {
    setCurrentDate(new Date());
  };

  /**
   * Format date for display
   */
  const formatDateDisplay = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      {/* Header */}
      <div className="flex flex-wrap justify-between items-center gap-4 mb-6">
        <div className="flex items-center gap-3">
          <CalendarIcon className="w-6 h-6 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">⏱ Timesheet Report</h1>
          <span className="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded-full">
            Total: {totalHours.toFixed(1)}h
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchTimesheets}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="Refresh"
          >
            <ArrowPathIcon className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Controls Bar */}
      <div className="flex flex-wrap items-center gap-4 mb-6 p-4 bg-gray-50 rounded-xl">
        {/* View Mode Toggle */}
        <div className="flex gap-1 border border-gray-200 rounded-lg overflow-hidden">
          <button
            onClick={() => setViewMode('week')}
            className={`px-4 py-2 text-sm transition-colors ${
              viewMode === 'week' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Week
          </button>
          <button
            onClick={() => setViewMode('month')}
            className={`px-4 py-2 text-sm transition-colors ${
              viewMode === 'month' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            Month
          </button>
        </div>

        {/* Date Navigation */}
        <div className="flex items-center gap-2">
          <button
            onClick={navigatePrevious}
            className="p-1.5 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <ChevronLeftIcon className="w-5 h-5" />
          </button>
          <span className="font-medium text-gray-800 min-w-[150px] text-center">
            {getDisplayRange()}
          </span>
          <button
            onClick={navigateNext}
            className="p-1.5 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <ChevronRightIcon className="w-5 h-5" />
          </button>
          <button
            onClick={goToToday}
            className="px-3 py-1 text-sm bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors"
          >
            Today
          </button>
        </div>

        <div className="flex-1"></div>

        {/* Export Button */}
        <div className="relative">
          <button
            onClick={() => setShowExportMenu(!showExportMenu)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 text-sm"
          >
            <DocumentArrowDownIcon className="w-4 h-4" />
            Export
            <ChevronDownIcon className="w-4 h-4" />
          </button>
          {showExportMenu && (
            <div className="absolute right-0 mt-2 w-44 bg-white rounded-lg shadow-lg border border-gray-200 z-10 overflow-hidden">
              <button
                onClick={exportToExcel}
                className="w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 text-left flex items-center gap-2"
              >
                📊 Excel (.xlsx)
              </button>
              <button
                onClick={exportToCSV}
                className="w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 text-left flex items-center gap-2"
              >
                📄 CSV (.csv)
              </button>
            </div>
          )}
        </div>

        {/* Import Button */}
        <div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xls,.csv"
            onChange={handleImport}
            className="hidden"
            id="import-file"
          />
          <label
            htmlFor="import-file"
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2 text-sm cursor-pointer"
          >
            <DocumentArrowUpIcon className="w-4 h-4" />
            Import
          </label>
        </div>
      </div>

      {/* Daily Summary */}
      {dailySummary.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <CalendarIcon className="w-12 h-12 mx-auto mb-2 opacity-30" />
          <p className="text-sm">No hours logged for this period</p>
        </div>
      ) : (
        <div className="space-y-4">
          {dailySummary.map((day) => (
            <div key={day.date} className="border rounded-xl overflow-hidden">
              <div className="flex justify-between items-center p-3 bg-gray-50 border-b">
                <div className="flex items-center gap-3">
                  <span className="font-medium text-gray-800">{formatDateDisplay(day.date)}</span>
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                    {day.entries.length} entries
                  </span>
                </div>
                <span className="font-semibold text-blue-600">{day.total_hours.toFixed(1)}h</span>
              </div>
              <div className="divide-y">
                {day.entries.map((entry) => (
                  <div key={entry.id} className="flex justify-between items-center p-3 hover:bg-gray-50 transition-colors">
                    <div>
                      <p className="text-sm font-medium text-gray-800">{entry.task_title}</p>
                      <p className="text-xs text-gray-400">
                        📁 {entry.project_name || 'Unknown'} 
                        {entry.project_id && <span className="ml-1">(ID: {entry.project_id})</span>}
                      </p>
                      <p className="text-xs text-gray-400">👤 {entry.user_name || 'Unknown'}</p>
                      {entry.description && (
                        <p className="text-xs text-gray-500">{entry.description}</p>
                      )}
                    </div>
                    <span className="text-sm text-gray-600">{entry.hours}h</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TimesheetReport;