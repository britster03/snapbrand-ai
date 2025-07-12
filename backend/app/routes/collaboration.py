from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from ..models import get_db, User, BrandProfile, TeamMember, ApprovalWorkflow, GeneratedImage
from ..core.auth import get_current_user
from ..services.notification import NotificationService

router = APIRouter(prefix="/collaboration", tags=["collaboration"])
notification_service = NotificationService()


# Pydantic models
class TeamMemberInvite(BaseModel):
    brand_profile_id: int
    user_email: str
    role: str = Field(..., pattern="^(admin|editor|viewer)$")
    permissions: Optional[List[str]] = Field(default_factory=list)


class TeamMemberResponse(BaseModel):
    id: int
    brand_profile_id: int
    user_id: str
    user_email: str
    user_name: str
    role: str
    permissions: List[str]
    invited_by: str
    invited_by_name: str
    joined_at: datetime

    class Config:
        from_attributes = True


class ApprovalRequest(BaseModel):
    generated_image_id: str
    brand_profile_id: int
    approvers: List[str]  # List of user IDs who need to approve
    comments: Optional[str] = None


class ApprovalAction(BaseModel):
    action: str = Field(..., pattern="^(approve|reject|revision)$")
    comments: Optional[str] = None
    revision_notes: Optional[str] = None


class ApprovalWorkflowResponse(BaseModel):
    id: int
    brand_profile_id: int
    generated_image_id: str
    requested_by: str
    requester_name: str
    status: str
    approvers: List[str]
    current_approver_index: int
    approval_history: List[dict]
    comments: Optional[str]
    revision_notes: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    image_url: Optional[str]
    image_prompt: Optional[str]

    class Config:
        from_attributes = True


@router.post("/team/invite", response_model=TeamMemberResponse)
async def invite_team_member(
    invite: TeamMemberInvite,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invite a team member to a brand profile."""
    
    # Verify brand ownership or admin role
    existing_member = db.query(TeamMember).filter_by(
        brand_profile_id=invite.brand_profile_id,
        user_id=current_user.id
    ).first()
    
    brand = db.query(BrandProfile).filter_by(id=invite.brand_profile_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    is_owner = brand.user_id == current_user.id
    is_admin = existing_member and existing_member.role == "admin"
    
    if not is_owner and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to invite team members")
    
    # Check if user exists
    invited_user = db.query(User).filter_by(email=invite.user_email).first()
    if not invited_user:
        raise HTTPException(status_code=404, detail="User not found. They must sign up first.")
    
    # Check if already a member
    existing = db.query(TeamMember).filter_by(
        brand_profile_id=invite.brand_profile_id,
        user_id=invited_user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User is already a team member")
    
    # Create team member
    team_member = TeamMember(
        brand_profile_id=invite.brand_profile_id,
        user_id=invited_user.id,
        role=invite.role,
        permissions=invite.permissions or [],
        invited_by=current_user.id
    )
    
    db.add(team_member)
    db.commit()
    db.refresh(team_member)
    
    # Send notification (async task in production)
    # notification_service.send_team_invite(invited_user.email, brand.name, current_user.username)
    
    return TeamMemberResponse(
        id=team_member.id,
        brand_profile_id=team_member.brand_profile_id,
        user_id=team_member.user_id,
        user_email=invited_user.email,
        user_name=invited_user.username,
        role=team_member.role,
        permissions=team_member.permissions or [],
        invited_by=team_member.invited_by,
        invited_by_name=current_user.username,
        joined_at=team_member.joined_at
    )


@router.get("/team/{brand_profile_id}", response_model=List[TeamMemberResponse])
async def list_team_members(
    brand_profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all team members for a brand profile."""
    
    # Verify access
    brand = db.query(BrandProfile).filter_by(id=brand_profile_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    # Check if user has access
    is_owner = brand.user_id == current_user.id
    is_member = db.query(TeamMember).filter_by(
        brand_profile_id=brand_profile_id,
        user_id=current_user.id
    ).first()
    
    if not is_owner and not is_member:
        raise HTTPException(status_code=403, detail="Not authorized to view team members")
    
    # Get all team members
    members = db.query(TeamMember).filter_by(brand_profile_id=brand_profile_id).all()
    
    # Include owner as implicit admin
    result = []
    
    # Add owner
    owner = db.query(User).filter_by(id=brand.user_id).first()
    if owner:
        result.append(TeamMemberResponse(
            id=0,  # Special ID for owner
            brand_profile_id=brand_profile_id,
            user_id=owner.id,
            user_email=owner.email,
            user_name=owner.username,
            role="owner",
            permissions=["all"],
            invited_by=owner.id,
            invited_by_name=owner.username,
            joined_at=brand.created_at
        ))
    
    # Add other members
    for member in members:
        user = db.query(User).filter_by(id=member.user_id).first()
        inviter = db.query(User).filter_by(id=member.invited_by).first()
        
        if user and inviter:
            result.append(TeamMemberResponse(
                id=member.id,
                brand_profile_id=member.brand_profile_id,
                user_id=member.user_id,
                user_email=user.email,
                user_name=user.username,
                role=member.role,
                permissions=member.permissions or [],
                invited_by=member.invited_by,
                invited_by_name=inviter.username,
                joined_at=member.joined_at
            ))
    
    return result


@router.put("/team/{member_id}")
async def update_team_member(
    member_id: int,
    role: Optional[str] = None,
    permissions: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update team member role and permissions."""
    
    member = db.query(TeamMember).filter_by(id=member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    # Verify authorization
    brand = db.query(BrandProfile).filter_by(id=member.brand_profile_id).first()
    is_owner = brand.user_id == current_user.id
    
    current_member = db.query(TeamMember).filter_by(
        brand_profile_id=member.brand_profile_id,
        user_id=current_user.id
    ).first()
    is_admin = current_member and current_member.role == "admin"
    
    if not is_owner and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update team members")
    
    # Update fields
    if role:
        member.role = role
    if permissions is not None:
        member.permissions = permissions
    
    db.commit()
    
    return {"message": "Team member updated successfully"}


@router.delete("/team/{member_id}")
async def remove_team_member(
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a team member from a brand profile."""
    
    member = db.query(TeamMember).filter_by(id=member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    # Verify authorization
    brand = db.query(BrandProfile).filter_by(id=member.brand_profile_id).first()
    is_owner = brand.user_id == current_user.id
    
    current_member = db.query(TeamMember).filter_by(
        brand_profile_id=member.brand_profile_id,
        user_id=current_user.id
    ).first()
    is_admin = current_member and current_member.role == "admin"
    
    # Users can remove themselves
    is_self = member.user_id == current_user.id
    
    if not is_owner and not is_admin and not is_self:
        raise HTTPException(status_code=403, detail="Not authorized to remove team members")
    
    db.delete(member)
    db.commit()
    
    return {"message": "Team member removed successfully"}


@router.post("/approval/request", response_model=ApprovalWorkflowResponse)
async def create_approval_request(
    request: ApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create an approval workflow for a generated image."""
    
    # Verify image exists and user has access
    image = db.query(GeneratedImage).filter_by(id=request.generated_image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Verify brand access
    brand = db.query(BrandProfile).filter_by(id=request.brand_profile_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    # Check if user is owner or team member
    is_owner = brand.user_id == current_user.id
    is_member = db.query(TeamMember).filter_by(
        brand_profile_id=request.brand_profile_id,
        user_id=current_user.id
    ).first()
    
    if not is_owner and not is_member:
        raise HTTPException(status_code=403, detail="Not authorized to create approval requests")
    
    # Verify approvers are valid team members
    for approver_id in request.approvers:
        is_approver_owner = brand.user_id == approver_id
        is_approver_member = db.query(TeamMember).filter_by(
            brand_profile_id=request.brand_profile_id,
            user_id=approver_id
        ).first()
        
        if not is_approver_owner and not is_approver_member:
            raise HTTPException(
                status_code=400,
                detail=f"User {approver_id} is not a team member"
            )
    
    # Create approval workflow
    workflow = ApprovalWorkflow(
        brand_profile_id=request.brand_profile_id,
        generated_image_id=request.generated_image_id,
        requested_by=current_user.id,
        approvers=request.approvers,
        current_approver_index=0,
        approval_history=[],
        comments=request.comments,
        status="pending"
    )
    
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    
    # Send notification to first approver (async in production)
    # first_approver = db.query(User).filter_by(id=request.approvers[0]).first()
    # if first_approver:
    #     notification_service.send_approval_request(
    #         first_approver.email,
    #         current_user.username,
    #         brand.name
    #     )
    
    return ApprovalWorkflowResponse(
        id=workflow.id,
        brand_profile_id=workflow.brand_profile_id,
        generated_image_id=workflow.generated_image_id,
        requested_by=workflow.requested_by,
        requester_name=current_user.username,
        status=workflow.status,
        approvers=workflow.approvers,
        current_approver_index=workflow.current_approver_index,
        approval_history=workflow.approval_history or [],
        comments=workflow.comments,
        revision_notes=workflow.revision_notes,
        created_at=workflow.created_at,
        completed_at=workflow.completed_at,
        image_url=image.s3_url,
        image_prompt=image.prompt
    )


@router.get("/approval/pending", response_model=List[ApprovalWorkflowResponse])
async def get_pending_approvals(
    brand_profile_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pending approval requests for the current user."""
    
    # Build query
    query = db.query(ApprovalWorkflow).filter(
        ApprovalWorkflow.status == "pending"
    )
    
    if brand_profile_id:
        query = query.filter(ApprovalWorkflow.brand_profile_id == brand_profile_id)
    
    # Get all pending approvals
    all_pending = query.all()
    
    # Filter to those where current user is the current approver
    user_pending = []
    for workflow in all_pending:
        if (workflow.approvers and 
            workflow.current_approver_index < len(workflow.approvers) and
            workflow.approvers[workflow.current_approver_index] == current_user.id):
            user_pending.append(workflow)
    
    # Build response
    result = []
    for workflow in user_pending:
        requester = db.query(User).filter_by(id=workflow.requested_by).first()
        image = db.query(GeneratedImage).filter_by(id=workflow.generated_image_id).first()
        
        if requester and image:
            result.append(ApprovalWorkflowResponse(
                id=workflow.id,
                brand_profile_id=workflow.brand_profile_id,
                generated_image_id=workflow.generated_image_id,
                requested_by=workflow.requested_by,
                requester_name=requester.username,
                status=workflow.status,
                approvers=workflow.approvers,
                current_approver_index=workflow.current_approver_index,
                approval_history=workflow.approval_history or [],
                comments=workflow.comments,
                revision_notes=workflow.revision_notes,
                created_at=workflow.created_at,
                completed_at=workflow.completed_at,
                image_url=image.s3_url,
                image_prompt=image.prompt
            ))
    
    return result


@router.post("/approval/{workflow_id}/action")
async def process_approval_action(
    workflow_id: int,
    action: ApprovalAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process an approval action (approve/reject/revision)."""
    
    workflow = db.query(ApprovalWorkflow).filter_by(id=workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Approval workflow not found")
    
    # Verify current user is the current approver
    if (not workflow.approvers or 
        workflow.current_approver_index >= len(workflow.approvers) or
        workflow.approvers[workflow.current_approver_index] != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to approve this request")
    
    # Add to approval history
    if not workflow.approval_history:
        workflow.approval_history = []
    
    workflow.approval_history.append({
        "user_id": current_user.id,
        "user_name": current_user.username,
        "action": action.action,
        "comments": action.comments,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Process action
    if action.action == "approve":
        # Move to next approver or complete
        workflow.current_approver_index += 1
        
        if workflow.current_approver_index >= len(workflow.approvers):
            # All approved
            workflow.status = "approved"
            workflow.completed_at = datetime.utcnow()
        else:
            # Notify next approver (async in production)
            pass
    
    elif action.action == "reject":
        workflow.status = "rejected"
        workflow.completed_at = datetime.utcnow()
    
    elif action.action == "revision":
        workflow.status = "revision"
        workflow.revision_notes = action.revision_notes
        # Notify requester (async in production)
    
    db.commit()
    
    return {
        "message": f"Approval {action.action} processed successfully",
        "status": workflow.status,
        "completed": workflow.status in ["approved", "rejected"]
    }


@router.get("/approval/history/{brand_profile_id}", response_model=List[ApprovalWorkflowResponse])
async def get_approval_history(
    brand_profile_id: int,
    status: Optional[str] = Query(None, pattern="^(pending|approved|rejected|revision)$"),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get approval workflow history for a brand."""
    
    # Verify access
    brand = db.query(BrandProfile).filter_by(id=brand_profile_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    
    is_owner = brand.user_id == current_user.id
    is_member = db.query(TeamMember).filter_by(
        brand_profile_id=brand_profile_id,
        user_id=current_user.id
    ).first()
    
    if not is_owner and not is_member:
        raise HTTPException(status_code=403, detail="Not authorized to view approval history")
    
    # Build query
    query = db.query(ApprovalWorkflow).filter_by(brand_profile_id=brand_profile_id)
    
    if status:
        query = query.filter(ApprovalWorkflow.status == status)
    
    # Get workflows
    workflows = query.order_by(ApprovalWorkflow.created_at.desc()).limit(limit).all()
    
    # Build response
    result = []
    for workflow in workflows:
        requester = db.query(User).filter_by(id=workflow.requested_by).first()
        image = db.query(GeneratedImage).filter_by(id=workflow.generated_image_id).first()
        
        if requester and image:
            result.append(ApprovalWorkflowResponse(
                id=workflow.id,
                brand_profile_id=workflow.brand_profile_id,
                generated_image_id=workflow.generated_image_id,
                requested_by=workflow.requested_by,
                requester_name=requester.username,
                status=workflow.status,
                approvers=workflow.approvers,
                current_approver_index=workflow.current_approver_index,
                approval_history=workflow.approval_history or [],
                comments=workflow.comments,
                revision_notes=workflow.revision_notes,
                created_at=workflow.created_at,
                completed_at=workflow.completed_at,
                image_url=image.s3_url,
                image_prompt=image.prompt
            ))
    
    return result