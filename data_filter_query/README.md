Of course. Here is a more detailed and example-rich user guide, written in Markdown. It's designed to be very clear for non-technical users, with multiple examples for every concept.

---

# A Simple Guide to Filtering Your Data

You can use the search bar to find exactly the information you need by typing in simple filters. This guide will show you how to build filters from simple to advanced.

## The Basics: Field, Operator, Value

Every filter you write has three simple parts: a **Field**, an **Operator**, and a **Value**.

```
  Field      Operator       Value
    |           |             |
  status        =        'COMPLETED'
```

*   **Field:** The piece of information you want to check (e.g., `status`, `client_id`, `our_deadline`).
*   **Operator:** The action you want to perform (e.g., `is`, `is not`, `contains`, `>`).
*   **Value:** The data you are looking for (e.g., `'COMPLETED'`, `123`, `yes`).

---

## Part 1: Operators (The "Actions")

Here are the most common operators you can use to build your filters.

| What you want to do | Operator(s) you can use |
| :--- | :--- |
| **Checking for Equality** | |
| Is exactly equal to | `=`, `==`, `is`, `eq` |
| Is *not* equal to | `!=`, `not`, `is not` |
| **Searching Within Text** | |
| Contains the text (case-insensitive) | `*=` or `icontains` |
| Starts with the text (case-insensitive) | `^=` or `istartswith` |
| Ends with the text (case-insensitive) | `$=` or `iendswith` |
| **Comparing Numbers or Dates** | |
| Greater than | `>` or `gt` |
| Greater than or equal to | `>=` or `gte` |
| Less than | `<` or `lt` |
| Less than or equal to | `<=` or `lte` |
| **Checking a List of Options** | |
| Is one of several options | `in` |
| Is *not* one of several options | `not in`|
| **Checking for Existence** | |
| The field is empty (has no value) | `is null` |
| The field is *not* empty | `not null` |

### Operator Examples

#### Equality Operators
*   Find all records with the status "COMPLETED":
    ```
    status = 'COMPLETED'
    ```
*   Find all records where the payment status is **not** "PAID":
    ```
    payment_status is not 'PAID'
    ```

#### Text Search Operators
*   Find remarks that contain the word "urgent":
    ```
    remarks *= 'urgent'
    ```
*   Find any client whose name contains "ltd":
    ```
    client_id__client_name *= 'ltd'
    ```
*   Find clients whose names start with "River":
    ```
    client_id__client_name ^= 'River'
    ```
*   Find all staff members whose first name starts with "J":
    ```
    assigned_to__first_name ^= 'J'
    ```
*   Find all staff members with a company email address:
    ```
    updated_by__email $= '@company.com'
    ```
*   Find records where the remarks end with a question mark:
    ```
    remarks $= '?'
    ```

#### Comparison Operators (for Numbers and Dates)
*   Find records with a charged amount greater than 1000:
    ```
    charged_amount > 1000
    ```
*   Find records where the balance is zero or less (paid or overpaid):
    ```
    balance_amount <= 0
    ```
*   Find all submissions with a deadline on or after Christmas 2025:
    ```
    HMRC_deadline >= '2025-12-25'
    ```
*   Find all submissions whose accounting period ended before June 2024:
    ```
    period < '2024-06-01'
    ```

#### List Operators
*   Find records where the status is either "PROCESSING" or "COMPLETED":
    ```
    status in ['PROCESSING', 'COMPLETED']
    ```
*   Find records that are **not** in the "WAITING" or "REQUESTED" statuses:
    ```
    status not in ['WAITING FOR INFORMATION', 'DOCUMENT REQUESTED']
    ```

#### Existence Operators
*   Find records where no one has been assigned yet:
    ```
    assigned_to is null
    ```
*   Find records where a submission date has been entered (is not empty):
    ```
    submission_date not null
    ```
---

## Part 2: Value Types (Formatting Your Data)

The `value` part of your filter needs to be formatted correctly.

### 1. Text (Strings)
When searching for text, you **must wrap it in single `' '` or double `"` quotes**.

*   `status = 'WAITING FOR INFORMATION'`
*   `remarks *= "client called"`

### 2. Numbers
Numbers (both whole and decimal) should be written **without** quotes.

*   `submission_id = 1024`
*   `charged_amount >= 499.99`

### 3. Yes / No (True / False)
For fields that are a "yes" or "no" checkbox, you can use any of the following friendly words **without** quotes.

*   **For "Yes" (True):** `true`, `yes`, `y`
*   **For "No" (False):** `false`, `no`, `n`

*   Find all records that have been submitted to HMRC:
    ```
    is_submitted_hmrc = yes
    ```
*   Find all records where documents have **not** been uploaded:
    ```
    is_documents_uploaded = false
    ```

### 4. Dates
Dates should be written as text inside quotes, using the `YYYY-MM-DD` format.

*   `our_deadline = '2025-11-15'`
*   `period_start_date >= '2024-01-01'`

### 5. Empty or Not Set (Null)
To find items where a field has no value, use one of these keywords **without** quotes.

*   `null`, `none`, `na`, `n/a`

*   Find records where the payment method has not been set:
    ```
    payment_method is null
    ```
*   Find all records that have a remark (the remarks field is not empty):
    ```
    remarks not null
    ```

### 6. A List of Items
To check against multiple values, use `in` or `not in` and put the values in square brackets `[ ]`, separated by commas. Remember to quote text values inside the list!

*   `status in ['PROCESSING', 'COMPLETED', 'EXTENDED']`
*   `submission_id in [101, 205, 311]`

---

## Part 3: Combining and Grouping Filters

### Combining with `AND`
Use `and` to find items that match **all** your conditions.

*   Find records that are "COMPLETED" **and** have been fully "PAID":
    ```
    status = 'COMPLETED' and payment_status = 'PAID'
    ```
*   Find records submitted after a certain date **and** where documents were uploaded:
    ```
    submission_date > '2025-01-01' and is_documents_uploaded = yes
    ```
**Shortcut:** If you don't type `and` between two filters, the system will assume you mean `and`.
```
is_submitted = yes payment_status = 'PAID'
```

### Combining with `OR`
Use `or` to find items that match **at least one** of your conditions.

*   Find all records where the payment status is "NOT PAID" **or** there is a balance remaining:
    ```
    payment_status = 'NOT PAID' or balance_amount > 0
    ```
*   Find records assigned to either Jane or John:
    ```
    assigned_to__first_name = 'Jane' or assigned_to__first_name = 'John'
    ```

### Grouping with Parentheses `()`
Use parentheses `()` to group conditions and control the order, especially when mixing `and` and `or`.

**Example Goal:** Find all submissions that are `EXTENDED`, **OR** submissions that are `COMPLETED` and also fully `PAID`.

```
status = 'EXTENDED' or (status = 'COMPLETED' and payment_status = 'PAID')
```
*   The parentheses ensure the `and` part is evaluated first (finding the "completed and paid" group).
*   The search then returns anything that is `EXTENDED` **or** anything that belongs to that group.

---

## Putting It All Together: A Complex Example

**Goal:** Find all submissions that are **not** yet completed, have a deadline in the last half of 2025, and are assigned to either Jane or John.

```
status != 'COMPLETED' and (HMRC_deadline >= '2025-07-01' and HMRC_deadline <= '2025-12-31') and assigned_to__first_name in ['Jane', 'John']
```

This query shows how you can combine all the concepts to build a very specific and powerful filter.
