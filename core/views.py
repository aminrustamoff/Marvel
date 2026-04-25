from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from .models import ListeningTest, ReadingTest, ResultsTable, ListeningResults, ReadingResults, WritingResults
import uuid
from .utils.text_to_html import convert
from .utils.normilizer import prepare
from .utils.marker import get_listening_band


from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import status # type: ignore

def home(request):
    return render(request, 'core/home.html')

def main(request):
    if request.method == "POST":
        unique_session = str(uuid.uuid4()).replace('-', '')[:16] 
        user_name = request.POST.get('username', '').strip() or 'Anonymous'

        new_entry = ResultsTable.objects.create(
            session_id=unique_session,
            username=user_name,
        )

        request.session['current_exam_id'] = new_entry.session_id
        return redirect('main')
    session_id = request.session.get('current_exam_id')
    context = {
        'listening_done': False,
        'reading_done': False,
        'writing_done': False,
        'username': '',
    }
    if session_id:
        try:
            session = ResultsTable.objects.get(session_id=session_id)
            context['username'] = session.username
            context['listening_done'] = ListeningResults.objects.filter(session=session).exists()
            context['reading_done'] = ReadingResults.objects.filter(session=session).exists()
            context['writing_done'] = WritingResults.objects.filter(session=session).exists()
        except ResultsTable.DoesNotExist:
            pass
    return render(request, 'core/main.html', context)

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

def reading(request, pk):

    reading_test = get_object_or_404(ReadingTest, pk=pk)

    passage_1_html = convert(reading_test.passage_1 or '')
    passage_2_html = convert(reading_test.passage_2 or '')
    passage_3_html = convert(reading_test.passage_3 or '')
    passage_1_test_html = convert(reading_test.passage_1_test or '')
    passage_2_test_html = convert(reading_test.passage_2_test or '')
    passage_3_test_html = convert(reading_test.passage_3_test or '')

    return render(request, 'core/reading.html', {
        'passage_1_html' : passage_1_html,
        'passage_2_html' : passage_2_html,
        'passage_3_html' : passage_3_html,
        'passage_1_test_html' : passage_1_test_html,
        'passage_2_test_html' : passage_2_test_html,
        'passage_3_test_html' : passage_3_test_html,
    })


class SubmitListeningAnswersView(APIView):
    def post(self, request):
        data = request.data
        session_id = request.session.get('current_exam_id')

        if not session_id:
            return Response({"error": "No active session"}, status=status.HTTP_403_FORBIDDEN)

        if not isinstance(data, dict):
            return Response({"error": "Invalid format"}, status=status.HTTP_400_BAD_REQUEST)

        session_obj = get_object_or_404(ResultsTable, session_id=session_id)

        # Guard: don't let them resubmit
        if ListeningResults.objects.filter(session=session_obj).exists():
            return Response({"error": "Already submitted"}, status=status.HTTP_409_CONFLICT)

        test_id = data.get('id')
        if not test_id:
            return Response({"error": "Missing test id"}, status=status.HTTP_400_BAD_REQUEST)

        test_answers = get_object_or_404(ListeningTest, id=int(test_id))
        dict_answers = prepare(test_answers.answers)

        correct_count = 0
        for id_num in dict_answers:
            user_answer = data.get(id_num)          # .get() instead of [] — no KeyError
            if user_answer and user_answer in dict_answers[id_num]:
                correct_count += 1

        mark = get_listening_band(correct_count)

        ListeningResults.objects.create(
            session=session_obj,
            test=test_answers,
            listening_row_answers=data,
            listening_correct_count=correct_count,
            listening_mark=mark,
        )

        return Response({"message": "Submitted successfully"}, status=status.HTTP_200_OK)
    
class SubmitReadingAnswersView(APIView):

    def post(self, request):
        pass

class SubmitReadinWritingAnswersView(APIView):

    def post(self, request):
        pass
    

def view_results(request, session_id):
    results = get_object_or_404(ListeningResults, session__session_id=session_id)
    return render(request, 'core/results.html', {'results': results})
