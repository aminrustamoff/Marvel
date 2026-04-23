from django.shortcuts import render, HttpResponse, get_object_or_404
from .models import ListeningTest, ListeningSubmission
from .utils.text_to_html import convert
from .utils.normilizer import prepare


from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import status # type: ignore

from .models import ListeningSubmission

def home(request):
    return render(request, 'core/main.html')

def listening(request, pk):


    test = get_object_or_404(ListeningTest, pk=pk)

    section1_html = convert(test.section_1 or '')
    section2_html = convert(test.section_2 or '')
    section3_html = convert(test.section_3 or '')
    section4_html = convert(test.section_4 or '')

    duration = f'{test.duration // 60}:{test.duration % 60:02d}' if test.duration else '0:00'

    return render(request, 'core/listening.html', {
        'test': test,
        'section1_html': section1_html,
        'section2_html': section2_html,
        'section3_html': section3_html,
        'section4_html': section4_html,
        'duration': duration,
    })

def reading(request):
    return render(request, 'core/reading.html')

# def get_duration_display(self):
#     if self.duration:
#         mins, secs = divmod(self.duration, 60)
#         return f"{mins}:{secs:02d}"
#     return "0:00"


class SubmitAnswersView(APIView):

    def post(self, request):
        data = request.data  # this is already parsed JSON
        correct_count = 0

        if not isinstance(data, dict):
            return Response(
                {"error": "Invalid format"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # All the logic happens here
        test_answers = get_object_or_404(ListeningTest, id=int(data['id']))
        dict_answers = prepare(test_answers.answers)

        print(dict_answers, '\n')
        print(data, '\n')

        for id_num in dict_answers:
            for element in dict_answers[id_num]:
                if element == data[id_num]:
                    correct_count += 1
        
        print("The number of correct answers:", correct_count)


        submission = ListeningSubmission.objects.create(
            answers=data, correct_count=correct_count
        )


        # write your logic between
        return Response({
            "message": "Answers received successfully",
            "submission_id": submission.id
        }, status=status.HTTP_200_OK)

def view_results(request, submission_id):
    submission = get_object_or_404(ListeningSubmission, id=submission_id)
    return HttpResponse(f"""Your answers: {submission.answers} <br/> 
                        The number of cerrect answers you've found: {submission.correct_count}""")
