"""
API views for achievements app.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import UserBadge, UserMilestone, Milestone


class BadgesAPIView(APIView):
    """Get user badges."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_badges = UserBadge.objects.filter(user=request.user).select_related('badge')
        return Response({
            'badges': [{
                'id': ub.badge.id,
                'name': ub.badge.name,
                'description': ub.badge.description,
                'icon': ub.badge.icon,
                'rarity': ub.badge.rarity,
                'earned_at': ub.earned_at.isoformat(),
            } for ub in user_badges]
        })


class MilestonesAPIView(APIView):
    """Get user milestones."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_milestones = UserMilestone.objects.filter(user=request.user).select_related('milestone')
        return Response({
            'milestones': [{
                'id': um.milestone.id,
                'name': um.milestone.name,
                'description': um.milestone.description,
                'milestone_type': um.milestone.milestone_type,
                'milestone_value': um.milestone.milestone_value,
                'celebration_message': um.milestone.celebration_message,
                'achieved_at': um.achieved_at.isoformat(),
                'certificate_generated': um.certificate_generated,
            } for um in user_milestones]
        })


class CertificateAPIView(APIView):
    """Generate shareable certificate for milestone as PDF."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, milestone_id):
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
            from reportlab.pdfgen import canvas
            from io import BytesIO
            from django.http import HttpResponse
        except ImportError:
            return Response(
                {'error': 'reportlab is required. Install with: pip install reportlab'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        user_milestone = get_object_or_404(
            UserMilestone,
            user=request.user,
            milestone_id=milestone_id
        )
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#3B82F6'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        # Certificate content
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph("CERTIFICATE OF ACHIEVEMENT", title_style))
        story.append(Spacer(1, 0.5*inch))
        
        story.append(Paragraph(
            f"This is to certify that",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph(
            f"<b>{request.user.username}</b>",
            ParagraphStyle(
                'UserName',
                parent=styles['Heading2'],
                fontSize=20,
                textColor=colors.HexColor('#1a1a2e'),
                alignment=1
            )
        ))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph(
            f"has achieved the milestone",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph(
            f"<b>{user_milestone.milestone.name}</b>",
            ParagraphStyle(
                'MilestoneName',
                parent=styles['Heading2'],
                fontSize=18,
                textColor=colors.HexColor('#10B981'),
                alignment=1
            )
        ))
        story.append(Spacer(1, 0.5*inch))
        
        story.append(Paragraph(
            user_milestone.milestone.celebration_message,
            ParagraphStyle(
                'Message',
                parent=styles['Normal'],
                fontSize=12,
                alignment=1,
                textColor=colors.HexColor('#6b7280')
            )
        ))
        story.append(Spacer(1, 0.5*inch))
        
        story.append(Paragraph(
            f"Achieved on: {user_milestone.achieved_at.strftime('%B %d, %Y')}",
            ParagraphStyle(
                'Date',
                parent=styles['Normal'],
                fontSize=10,
                alignment=1,
                textColor=colors.HexColor('#9ca3af')
            )
        ))
        story.append(Spacer(1, 1*inch))
        
        story.append(Paragraph(
            "Ambitious Hub",
            ParagraphStyle(
                'Signature',
                parent=styles['Normal'],
                fontSize=12,
                alignment=1,
                textColor=colors.HexColor('#3B82F6')
            )
        ))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Mark as generated
        user_milestone.certificate_generated = True
        user_milestone.save()
        
        # Return PDF response
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="certificate_{milestone_id}.pdf"'
        return response

