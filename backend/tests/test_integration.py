"""
Integration tests covering multiple components.
"""
from fastapi import status


def test_complete_workflow(client, db_session, auth_headers, test_user, test_user2):
    """Test a complete workflow: project creation -> task -> comment -> timesheet."""
    
    # 1. Create a project
    response = client.post(
        "/api/v1/projects/",
        json={
            "name": "Integration Test Project",
            "description": "Testing full workflow"
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    project = response.json()
    project_id = project["id"]
    
    # 2. Add a member
    response = client.post(
        f"/api/v1/projects/{project_id}/members",
        json={
            "user_id": test_user2.id,
            "role": "Member"
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    
    # 3. Create a task
    response = client.post(
        "/api/v1/tasks/",
        json={
            "title": "Integration Task",
            "description": "Task for integration test",
            "project_id": project_id,
            "assignee_id": test_user2.id,
            "priority": "High"
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    task = response.json()
    task_id = task["id"]
    
    # 4. Add a comment
    response = client.post(
        f"/api/v1/comments/task/{task_id}",
        json={
            "content": "This is an integration test comment",
            "mentions": []
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    
    # 5. Update task status
    response = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        json={"status": "InProgress"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    # 6. Add timesheet
    from datetime import date
    response = client.post(
        "/api/v1/timesheets/",
        json={
            "task_id": task_id,
            "date": date.today().isoformat(),
            "hours": 3.0,
            "description": "Worked on integration task"
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    
    # 7. Check dashboard stats
    response = client.get(
        "/api/v1/dashboard/stats",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    stats = response.json()
    assert stats["total_projects"] >= 1
    assert stats["total_tasks"] >= 1