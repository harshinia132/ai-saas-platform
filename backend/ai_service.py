import google.generativeai as genai
import time

class AIService:
    def __init__(self):
        api_key = 'AIzaSyAGc_epA7-Pq_0lOV5J_o3csOArlgkqR3o'
        self.use_mock = False
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                model_name = 'models/gemini-2.5-flash'
                self.model = genai.GenerativeModel(model_name)
                self.is_available = True
                print(f"AI Service initialized with {model_name}")
            except Exception as e:
                print(f"AI init failed: {e}, using mock mode")
                self.use_mock = True
                self.is_available = False
                self.model = None
        else:
            print("No API key found, using mock mode")
            self.use_mock = True
            self.is_available = False
            self.model = None
    
    def summarize_meeting(self, transcript):
        # Always use mock if no model
        if self.use_mock or not self.model:
            return self._mock_summarize(transcript)
        
        try:
            prompt = f"Summarize this meeting in 3-4 sentences:\n\n{transcript}"
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"AI Error in summary: {e}")
            return self._mock_summarize(transcript)
    
    def extract_action_items(self, transcript):
        if self.use_mock or not self.model:
            return self._mock_action_items(transcript)
        
        try:
            prompt = f"Extract action items from this meeting as a numbered list:\n\n{transcript}"
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"AI Error in action items: {e}")
            return self._mock_action_items(transcript)
    
    def _mock_summarize(self, transcript):
        return """📋 Meeting Summary:
- Team discussed project priorities and timelines
- Authentication module needs 3 more days for completion
- Dashboard UI is ready for development
- Daily standup meetings scheduled at 10 AM
- Documentation needs to be updated by Friday"""
    
    def _mock_action_items(self, transcript):
        return """✅ Action Items:
1. Complete authentication API by Friday (Assigned to Backend Team)
2. Build dashboard UI by Monday (Assigned to Frontend Team)
3. Write unit tests by Wednesday (Assigned to QA Team)
4. Update API documentation by Friday (Assigned to Tech Writer)
5. Schedule code review meeting for Thursday"""
    
    def get_task_priority_suggestion(self, task_title, task_description):
        if self.use_mock or not self.model:
            if 'urgent' in task_title.lower() or 'critical' in task_description.lower():
                return "Urgent"
            elif 'important' in task_title.lower() or 'high' in task_description.lower():
                return "High"
            else:
                return "Medium"
        
        try:
            prompt = f"Analyze this task and suggest priority (Low/Medium/High/Urgent). Return only one word:\n\nTitle: {task_title}"
            response = self.model.generate_content(prompt)
            result = response.text.strip()
            for priority in ['Low', 'Medium', 'High', 'Urgent']:
                if priority.lower() in result.lower():
                    return priority
            return "Medium"
        except:
            return "Medium"
    
    def get_productivity_insight(self, completed_tasks_count, pending_tasks_count):
        if self.use_mock or not self.model:
            if pending_tasks_count > 5:
                return "🎯 You have many pending tasks. Try breaking them into smaller chunks and prioritize the most important ones first!"
            elif completed_tasks_count > 0:
                return "✅ Great progress! You've completed tasks. Keep up the momentum!"
            else:
                return "💡 Start with your most important task first thing tomorrow. Remember, small steps lead to big results!"
        
        try:
            prompt = f"Give one short productivity tip for someone with {completed_tasks_count} completed and {pending_tasks_count} pending tasks."
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return "Stay focused and prioritize your most important tasks!"
    
    def get_task_breakdown(self, task_title):
        if self.use_mock or not self.model:
            return f"""📝 Task Breakdown for "{task_title}":
1. Research and gather requirements
2. Design the solution architecture
3. Implement core functionality
4. Write tests
5. Review and refactor
6. Deploy and monitor"""
        
        try:
            prompt = f"Break down this task into 3-5 subtasks:\n\nTask: {task_title}\n\nReturn as a numbered list only."
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return self._mock_breakdown(task_title)
    
    def _mock_breakdown(self, task_title):
        return f"""📝 Task Breakdown for "{task_title}":
1. Analyze requirements
2. Design solution
3. Implement features
4. Test and validate
5. Deploy"""
