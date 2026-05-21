from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import MeetingSummary

# Import AI service with error handling
try:
    from ai_service import AIService
    ai_service = AIService()
    AI_AVAILABLE = True
except Exception as e:
    print(f"Failed to load AI service: {e}")
    AI_AVAILABLE = False
    ai_service = None

@login_required
def meeting_summarize(request):
    summary = None
    action_items = None
    recent_meetings = MeetingSummary.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    
    if request.method == 'POST':
        meeting_text = request.POST.get('meeting_text', '')
        meeting_title = request.POST.get('title', 'Untitled Meeting')
        
        if meeting_text:
            try:
                if ai_service:
                    # Generate summary using the service
                    summary = ai_service.summarize_meeting(meeting_text)
                    action_items = ai_service.extract_action_items(meeting_text)
                    
                    # Save to database
                    meeting = MeetingSummary.objects.create(
                        title=meeting_title,
                        transcript=meeting_text,
                        summary=summary,
                        action_items={'items': action_items},
                        created_by=request.user
                    )
                    messages.success(request, 'Meeting summarized successfully!')
                else:
                    # Mock response when AI not available
                    summary = """📋 Meeting Summary:
- Team discussed project priorities
- Multiple action items identified
- Next steps defined"""
                    action_items = """✅ Action Items:
1. Follow up on action items
2. Schedule next meeting
3. Update project documentation"""
                    messages.warning(request, 'AI service unavailable. Using mock response.')
                    
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Please enter meeting text.')
    
    context = {
        'summary': summary,
        'action_items': action_items,
        'recent_meetings': recent_meetings,
        'ai_available': AI_AVAILABLE,
    }
    return render(request, 'meeting_ai/summarize.html', context)
