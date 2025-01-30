# Calendar System Documentation

## Overview

This document provides a detailed explanation of the calendar system implemented for tracking events related to trees, vegetables, and plants. It includes the JavaScript logic for event processing, rendering the calendar, and handling API requests via Django REST framework.

---

## Calendar Logic

The calendar visualizes agricultural events such as planting, fertilizing, blooming, ripening, and pruning. Events are color-coded and arranged to prevent overlapping of the same event type on the same date.

### **Key Features:**

- Fetches plant varieties based on category selection (trees, vegetables, plants).
- Retrieves detailed event data for selected varieties.
- Prevents duplicate overlapping events of the same type.
- Displays a legend to indicate event colors.
- Utilizes **Moment.js** for date management.
- Generates a yearly view with month-based grids.

### **Event Categories & Colors:**

| Event Type                 | Color Code           |
| -------------------------- | -------------------- |
| Цвітіння (Blooming)        | #D50000 (Red)        |
| Дозрівання (Ripening)      | #2962FF (Blue)       |
| Посів (Sowing)             | #4CAF50 (Green)      |
| Зрілість (Maturity)        | #2E7D32 (Dark Green) |
| Садіння рослини (Planting) | #8E24AA (Purple)     |
| Удобрення (Fertilization)  | #FF6D00 (Orange)     |
| Обрізка (Pruning)          | #212121 (Dark Gray)  |

### **JavaScript Logic:**

1. **Fetching Sorts:**
   - Retrieves available sorts based on the selected category.
2. **Fetching Sort Details:**
   - Requests detailed event data for the selected sort.
   - Formats event data and initializes the calendar.
3. **Event Formatting:**
   - Ensures each event type is unique per date to prevent overlapping colors.
4. **Calendar Initialization:**
   - Creates a yearly view, displaying events as color strips in date cells.
   - Generates a legend mapping event types to colors.

---

## API Endpoints

### **1. ****`get_sorts`**** (POST)**

**URL:** `/api/get_sorts/`
**Description:** Retrieves available sorts for a given category.

#### **Request Body:**

```json
{
    "category": "дерева" | "овочі" | "рослини"
}
```

#### **Response:**

```json
["Sort1", "Sort2", "Sort3"]
```

#### **Error Responses:**

- `400 Bad Request` if category is unknown.
- `500 Internal Server Error` for unexpected failures.

---

### **2. ****`get_sort_details`**** (POST)**

**URL:** `/api/get_sort_details/`
**Description:** Fetches event details for the selected sort.

#### **Request Body:**

```json
{
    "category": "дерева",
    "sort_name": "Apple Tree"
}
```

#### **Response Example:**

```json
{
    "Scope_of_bloom_From": "04-01",
    "Scope_of_bloom_To": "04-15",
    "Ripe_Time_From": "09-10",
    "Ripe_Time_To": "09-30",
    "Planting_time_From1": "03-15",
    "Planting_time_To1": "04-10",
    "Cutting_time_From1": "02-20",
    "Cutting_time_To1": "03-05",
    "Fertilizer_date_From1_1": "05-01",
    "Fertilizer_date_To1_1": "05-10"
}
```


