# Module 1 – User Authentication Testing

## Test Execution Results

| Test ID| Test Scenario               | Expected Result                        | Actual Result                    | Status|
|--------|-----------------------------|----------------------------------------|----------------------------------|-------|
| TC01   | Open Profile Page           | Profile page should load successfully  | Profile page loaded successfully | PASS  |
| TC02   | View Profile Details        | User details should be displayed       | User details displayed correctly | PASS  |
| TC03   | Update Bio                  | Bio should be saved successfully       | Bio saved successfully           | PASS  |
| TC04   | Refresh Profile             | Updated bio should remain visible      | Updated bio remained visible     | PASS  |
| TC05   | Logout                      | User should be logged out              | Logout successful                | PASS  |
| TC06   | Access Profile Without Login| User should be redirected to login page| Redirected to login page         | PASS  |
| TC07   | Login with Invalid Password | Error message should be displayed      | Error message displayed          | PASS  |
| TC08   | Login with Correct Password | User should log in successfully        | Login successful                 | PASS  |

## Summary

- Total Test Cases: 8
- Passed: 8
- Failed: 0
- Blocked: 0

**Overall Status: PASS**



# Module 2 – Social Feed Testing

## Test Execution Results

| Test ID | Test Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC09 | Open Feed | Feed page should load successfully | Feed loaded successfully | PASS |
| TC10 | Create a Text Post | Post should be published successfully | Post published successfully | PASS |
| TC11 | View Published Post | Published post should appear in feed | Post appeared in feed | PASS |
| TC12 | Refresh Feed | Published post should remain visible | Post remained visible | PASS |
| TC13 | Create Empty Post | Empty post should not be published | Empty post was rejected | PASS |
| TC14 | Create Long Post | System should handle long content appropriately | Long post was rejected | PASS |
| TC15 | Like a Post | Post should get liked | Post liked successfully | PASS |
| TC16 | Unlike a Post | Like should be removed | Like removed successfully | PASS |
| TC17 | Like Count | Like count should update correctly | Like count updated correctly | PASS |
| TC18 | Comment on a Post | User should be able to comment | Comment feature unavailable | N/A |
| TC19 | Edit a Post | User should be able to edit a post | Edit option unavailable | N/A |
| TC20 | Delete a Post | User should be able to delete a post | Delete option unavailable | N/A |
| TC21 | Navigate Away and Return | Published post should remain visible | Post remained visible | PASS |
| TC22 | Multiple Posts | Multiple posts should appear in feed | Both posts appeared successfully | PASS |
| TC23 | Post Order | Latest post should appear first | Latest post appeared first | PASS |
| TC24 | Post Persistence | Posts should remain available after re-login | Posts remained visible after re-login | PASS |
| TC25 | Like Status After Refresh | Like status should remain correct | Like status remained correct | PASS |
| TC26 | Feed Scrolling | User should be able to scroll through posts | Feed scrolling worked correctly | PASS |
| TC27 | Spaces-only Post | Spaces-only post should not be published | Spaces-only post was rejected | PASS |
| TC28 | Post Without Login | Unauthenticated users should not be able to publish posts | Post publishing was prevented | PASS |

## Module 2 – Summary

- Total Test Cases: 20
- Passed: 17
- Failed: 0
- Not Applicable: 3

**Overall Status: PASS**

## Observations

- Feed and post creation functionalities worked successfully.
- Like and unlike functionalities worked correctly.
- Post ordering and persistence worked correctly.
- Empty and spaces-only posts were rejected.
- Long post submission was rejected.
- Comment, edit and delete options were unavailable during testing.
