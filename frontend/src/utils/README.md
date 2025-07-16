# Date Utility Functions

This directory contains utility functions for consistent date formatting across the frontend application.

## Functions

### `formatToIST(dateString)`
Formats a date string to **dd/mm/yyyy hh:mm:ss IST** in 24-hour format.

**Parameters:**
- `dateString` (string): A valid date string or Date object

**Returns:**
- `string`: Formatted date string in dd/mm/yyyy hh:mm:ss IST format
- `string`: Empty string if invalid date

**Example:**
```javascript
import { formatToIST } from '../utils/dateUtils';

formatToIST('2024-12-25T14:30:45Z');
// Returns: "25/12/2024 20:00:45 IST"
```

### `formatDateOnly(dateString)`
Formats a date string to **dd/mm/yyyy** only.

**Parameters:**
- `dateString` (string): A valid date string or Date object

**Returns:**
- `string`: Formatted date string in dd/mm/yyyy format
- `string`: Empty string if invalid date

**Example:**
```javascript
import { formatDateOnly } from '../utils/dateUtils';

formatDateOnly('2024-12-25T14:30:45Z');
// Returns: "25/12/2024"
```

## Usage

Import the functions in your component:

```javascript
import { formatToIST, formatDateOnly } from '../utils/dateUtils';

// Use in your JSX
<span>Last updated: {formatToIST(lastUpdated)}</span>
<span>Added date: {formatDateOnly(item.added_date)}</span>
```

## Features

- ✅ Converts to IST timezone (UTC+5:30)
- ✅ 24-hour format
- ✅ Consistent dd/mm/yyyy format
- ✅ Handles invalid dates gracefully
- ✅ Zero-padded numbers
- ✅ IST suffix for clarity 