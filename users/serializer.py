from rest_framework import serializers
from .models import Profile, CustomUser


# for ProfileSerializer we need their username so lets create custom field using SerializerMethodField
class ProfileSerializer(serializers.ModelSerializer):
    # creating the SerializerMethodField and grabbing value from function called get_username
    # REMOVED: trailing fields for easy index display on front end
    username = serializers.SerializerMethodField('get_username')
    feedback = serializers.SerializerMethodField('get_feedback')
    bugs = serializers.SerializerMethodField('get_bugs')
    is_staff = serializers.SerializerMethodField('get_is_staff')

    def get_username(self, profile):
        # Profile getting the instance we can use to retrieve the username
        username = profile.user.username
        return username

    def get_feedback(self, profile):
        # We are going to return feedback which could be null so
        if profile.feedback_set.first():
            feedback = profile.feedback_set.first()
            answers = {ans.question.questions: ans.get_written_ans() for ans in feedback.feedbackanswers_set.all()}
            feedback_detail = {
                'opinions': feedback.opinions,
                'suggestions': feedback.suggestions,
                'answers': answers
            }
            return feedback_detail
        return None

    def get_bugs(self, profile):
        # we know that profile has the same id has customuser
        user = CustomUser.objects.get(id=profile.id)
        # now that we have our user we could trace back the foreign key in submit bugs
        if user.submitbug_set.first():
            all_bugs = []
            # we cannot return a Object type SubmitBug because it is not JSON serializable so
            for bug in user.submitbug_set.all():
                # we need to loop through all of them to create a
                json_bug = {
                    'bug_id': bug.id,
                    'bug_owner_name': bug.bug_owner_name,
                    'bug_message': bug.bug_message,
                    'date_added': bug.date_added
                }
                if bug.bug_owner:
                    json_bug['bug_owner'] = bug.bug_owner.id    # make sure its the id not the CustomUser obj
                elif bug.bug_image:
                    json_bug['bug_image'] = bug.bug_image
                all_bugs.append(json_bug)
            return all_bugs
        return None

    def get_is_staff(self, profile):
        return profile.user.is_staff

    class Meta:
        # Make sure you dont have , after Profile because ERROR: restframework 'tuple' object has no attribute '_meta'
        model = Profile
        fields = (
            'username',
            'is_staff',
            'date_joined',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'card',
            'address',
            'city',
            'country',
            'state',
            'zip_code',
            'feedback',
            'bugs'
        )