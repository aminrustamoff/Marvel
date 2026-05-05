from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from .models import ListeningTest, ReadingTest, WritingTask1, WritingTask2, ResultsTable, ListeningResults, ReadingResults, WritingResults, ExamSession
import uuid
import random
from .utils.text_to_html import convert
from .utils.normilizer import prepare
from .utils.marker import get_listening_band, get_reading_band


from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import status # type: ignore

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.platypus.flowables import PageBreak

from .models import (
    ExamSession,
    ResultsTable,
    ListeningResults,
    ReadingResults,
    WritingResults
)

# Qeustion ID randomizer variables

first_time = True
listening_id_random = 0
reading_id_random = 0
writing_1_id_random = 0
writing_2_id_random = 0


def home(request):
    exam_sessions = ExamSession.objects.filter(is_open=True)
    return render(request, 'core/home.html', {'exam_sessions' : exam_sessions})

def main(request):
    if request.method == "POST":
        unique_session = str(uuid.uuid4()).replace('-', '')[:16] 
        user_name = request.POST.get('username', '').strip() or 'Anonymous'

        exam_session_id = request.POST.get('exam_session')

        exam_session = get_object_or_404(
            ExamSession,
            id=exam_session_id
        )

        new_entry = ResultsTable.objects.create(
            session_id=unique_session,
            username=user_name,
            exam_session = exam_session,
        )

        request.session['current_exam_id'] = new_entry.session_id
        return redirect('main')
    
    global first_time
    if first_time:
        global listening_id_random
        global reading_id_random
        global writing_1_id_random
        global writing_2_id_random

        first_time = False
        
        l_ids = list(ListeningTest.objects.filter(is_active=True).values_list('id', flat=True))
        r_ids = list(ReadingTest.objects.filter(is_active=True).values_list('id', flat=True))
        w1_ids = list(WritingTask1.objects.filter(is_active=True).values_list('id', flat=True))
        w2_ids = list(WritingTask2.objects.filter(is_active=True).values_list('id', flat=True))

        listening_id_random = random.choice(l_ids) if l_ids else None
        reading_id_random = random.choice(r_ids) if r_ids else None
        writing_1_id_random = random.choice(w1_ids) if w1_ids else None
        writing_2_id_random = random.choice(w2_ids) if w2_ids else None

    session_id = request.session.get('current_exam_id')
    context = {
        'session_id' : session_id,
        'listening_id_random': listening_id_random,
        'reading_id_random': reading_id_random,
        'writing_1_id_random': writing_1_id_random,
        'writing_2_id_random': writing_2_id_random,
        'listening_done': False,
        'reading_done': False,
        'writing_done': False,
        'username': '',
    }
    if session_id:
        try:
            session = ResultsTable.objects.get(session_id=session_id)
            context['username'] = session.username
            context['exam_session'] = session.exam_session
            context['listening_done'] = ListeningResults.objects.filter(session=session).exists()
            context['reading_done'] = ReadingResults.objects.filter(session=session).exists()
            context['writing_done'] = WritingResults.objects.filter(session=session).exists()
        except ResultsTable.DoesNotExist:
            pass
    return render(request, 'core/main.html', context)

def listening(request, pk):


    test = get_object_or_404(ListeningTest, pk=pk)
    
    images = {img.label: img.image.url for img in test.images.all()}

    section1_html = convert(test.section_1 or '', images)
    section2_html = convert(test.section_2 or '', images)
    section3_html = convert(test.section_3 or '', images)
    section4_html = convert(test.section_4 or '', images)


    duration = f'{test.duration // 60}:{test.duration % 60:02d}' if test.duration else '0:00'

    session_id = request.session.get('current_exam_id')

    return render(request, 'core/listening.html', {
        'session_id' : session_id,
        'test': test,
        'section1_html': section1_html,
        'section2_html': section2_html,
        'section3_html': section3_html,
        'section4_html': section4_html,
        'duration': duration,
    })

def reading(request, pk):

    reading_test = get_object_or_404(ReadingTest, pk=pk)
    
    images = {img.label: img.image.url for img in reading_test.images.all()}

    passage_1_html = convert(reading_test.passage_1 or '', images)
    passage_2_html = convert(reading_test.passage_2 or '', images)
    passage_3_html = convert(reading_test.passage_3 or '', images)
    passage_1_test_html = convert(reading_test.passage_1_test or '', images)
    passage_2_test_html = convert(reading_test.passage_2_test or '', images)
    passage_3_test_html = convert(reading_test.passage_3_test or '', images)

    session_id = request.session.get('current_exam_id')

    return render(request, 'core/reading.html', {
        'session_id' : session_id,
        'test': reading_test,
        'passage_1_html' : passage_1_html,
        'passage_2_html' : passage_2_html,
        'passage_3_html' : passage_3_html,
        'passage_1_test_html' : passage_1_test_html,
        'passage_2_test_html' : passage_2_test_html,
        'passage_3_test_html' : passage_3_test_html,
    })

def writing(request, pk1, pk2):
    task_1 = get_object_or_404(WritingTask1, pk=pk1)
    task_2 = get_object_or_404(WritingTask2, pk=pk2)

    images = {img.label: img.image.url for img in task_1.images.all()}

    task_1_html = convert(task_1.question or '', images)
    task_2_html = convert(task_2.question or '')

    session_id = request.session.get('current_exam_id')

    return render(request, 'core/writing.html', {
        'session_id' : session_id,
        'test_id' : f'{pk1}-{pk2}',
        'task_1_html' : task_1_html,
        'task_2_html' : task_2_html,
    })

def finish(request):
    session_id = request.session.get('current_exam_id')
    if session_id:
        request.session.pop('current_exam_id')
    return render(request, 'core/finish.html')

def preview(request, section, pk):

    if section == 'listening':
        test = get_object_or_404(ListeningTest, pk=pk)
    
        images = {img.label: img.image.url for img in test.images.all()}

        section1_html = convert(test.section_1 or '', images)
        section2_html = convert(test.section_2 or '', images)
        section3_html = convert(test.section_3 or '', images)
        section4_html = convert(test.section_4 or '', images)

        content = {
                'test': test,
                'section1_html': section1_html,
                'section2_html': section2_html,
                'section3_html': section3_html,
                'section4_html': section4_html,
            }
        return render(request, 'core/pre-listening.html', content)

    elif section == 'reading':
        reading_test = get_object_or_404(ReadingTest, pk=pk)
    
        images = {img.label: img.image.url for img in reading_test.images.all()}

        passage_1_html = convert(reading_test.passage_1 or '', images)
        passage_2_html = convert(reading_test.passage_2 or '', images)
        passage_3_html = convert(reading_test.passage_3 or '', images)
        passage_1_test_html = convert(reading_test.passage_1_test or '', images)
        passage_2_test_html = convert(reading_test.passage_2_test or '', images)
        passage_3_test_html = convert(reading_test.passage_3_test or '', images)

        content = {
                'test': reading_test,
                'passage_1_html' : passage_1_html,
                'passage_2_html' : passage_2_html,
                'passage_3_html' : passage_3_html,
                'passage_1_test_html' : passage_1_test_html,
                'passage_2_test_html' : passage_2_test_html,
                'passage_3_test_html' : passage_3_test_html,
            }
        return render(request, 'core/pre-reading.html', content)

    elif section == 'writing-task-1':
        task_1 = get_object_or_404(WritingTask1, pk=pk)
        images = {img.label: img.image.url for img in task_1.images.all()}

        task_1_html = convert(task_1.question or '', images)

        return render(request, 'core/pre-writing-1.html', {
            'task_1_html': task_1_html,
        })

    elif section == 'writing-task-2':
        task_2 = get_object_or_404(WritingTask2, pk=pk)
        task_2_html = convert(task_2.question or '')

        return render(request, 'core/pre-writing-2.html', {
            'task_2_html': task_2_html,
        })

    else:
        return HttpResponse("Invalid section", status=400)  

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
        data = request.data
        session_id = request.session.get('current_exam_id')

        if not session_id:
            return Response({"error": "No active session"}, status=status.HTTP_403_FORBIDDEN)

        if not isinstance(data, dict):
            return Response({"error": "Invalid format"}, status=status.HTTP_400_BAD_REQUEST)

        session_obj = get_object_or_404(ResultsTable, session_id=session_id)

        # Guard: don't let them resubmit
        if ReadingResults.objects.filter(session=session_obj).exists():
            return Response({"error": "Already submitted"}, status=status.HTTP_409_CONFLICT)

        test_id = data.get('id')
        if not test_id:
            return Response({"error": "Missing test id"}, status=status.HTTP_400_BAD_REQUEST)
        
        reading_test = get_object_or_404(ReadingTest, id=int(test_id))
        dict_answers = prepare(reading_test.answers)
        correct_count = 0

        for id_num in dict_answers:
            user_answer = data.get(id_num)          # .get() instead of [] — no KeyError
            if user_answer and user_answer in dict_answers[id_num]:
                correct_count += 1

        mark = get_reading_band(correct_count)

        ReadingResults.objects.create(
            session=session_obj,
            test=reading_test,
            reading_row_answers=data,
            reading_correct_count=correct_count,
            reading_mark=mark,
        )

        return Response({"message": "Submitted successfully"}, status=status.HTTP_200_OK)

class SubmitWritingAnswersView(APIView):

    def post(self, request):
        data = request.data
        session_id = request.session.get('current_exam_id')

        if not session_id:
            return Response({"error": "No active session"}, status=status.HTTP_403_FORBIDDEN)

        if not isinstance(data, dict):
            return Response({"error": "Invalid format"}, status=status.HTTP_400_BAD_REQUEST)

        session_obj = get_object_or_404(ResultsTable, session_id=session_id)

        # Guard: don't let them resubmit
        if WritingResults.objects.filter(session=session_obj).exists():
            return Response({"error": "Already submitted"}, status=status.HTTP_409_CONFLICT)

        test_id = data.get('id')
        if not test_id:
            return Response({"error": "Missing test id"}, status=status.HTTP_400_BAD_REQUEST)
        
        WritingResults.objects.create(
            session=session_obj,
            test_id=test_id,
            task1_text=data.get('report', ''),
            task1_word_count=data.get('word_count_report', 0),
            task2_text=data.get('essay', ''),
            task2_word_count=data.get('word_count_essay', 0),
        )

        return Response({"message": "Submitted successfully"}, status=status.HTTP_200_OK)
    

def view_results(request):

    sessions = ExamSession.objects.all().order_by('-created_at')

    return render(request, 'core/results.html', {
        'sessions': sessions
    })


def view_results_detail(request, session_id):

    exam_session = get_object_or_404(
        ExamSession,
        id=session_id
    )

    results = ResultsTable.objects.filter(
        exam_session=exam_session
    ).order_by('-session_date')

    students = []

    for index, result in enumerate(results, start=1):

        listening = ListeningResults.objects.filter(
            session=result
        ).first()

        reading = ReadingResults.objects.filter(
            session=result
        ).first()

        writing = WritingResults.objects.filter(
            session=result
        ).first()

        students.append({
            'number': index,
            'result': result,
            'listening': listening,
            'reading': reading,
            'writing': writing,
        })

    return render(request, 'core/results_detail.html', {
        'exam_session': exam_session,
        'students': students,
    })

def student_full_result(request, session_id):

    result = get_object_or_404(
        ResultsTable,
        session_id=session_id
    )

    listening = ListeningResults.objects.filter(
        session=result
    ).first()

    reading = ReadingResults.objects.filter(
        session=result
    ).first()

    writing = WritingResults.objects.filter(
        session=result
    ).first()

    return render(request, 'core/student_full_result.html', {
        'result': result,
        'listening': listening,
        'reading': reading,
        'writing': writing,
    })

def download_session_pdf(request, session_id):

    exam_session = get_object_or_404(
        ExamSession,
        id=session_id
    )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        f'attachment; filename="{exam_session.name}.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=18
    )

    styles = getSampleStyleSheet()

    elements = []

    # Title

    title = Paragraph(
        f"<b>{exam_session.name} - Results</b>",
        styles['Title']
    )

    elements.append(title)
    elements.append(Spacer(1, 20))

    # Table Data

    data = [[
        'No',
        'Full Name',
        'Listening',
        'Reading'
    ]]

    results = ResultsTable.objects.filter(
        exam_session=exam_session
    )

    for index, result in enumerate(results, start=1):

        listening = ListeningResults.objects.filter(
            session=result
        ).first()

        reading = ReadingResults.objects.filter(
            session=result
        ).first()

        listening_score = (
            str(listening.listening_mark)
            if listening else '-'
        )

        reading_score = (
            str(reading.reading_mark)
            if reading else '-'
        )

        data.append([
            str(index),
            result.username,
            listening_score,
            reading_score
        ])

    table = Table(data, colWidths=[50, 220, 100, 100])

    table.setStyle(TableStyle([

        ('BACKGROUND', (0, 0), (-1, 0), colors.black),

        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),

        ('GRID', (0, 0), (-1, -1), 1, colors.grey),

        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),

    ]))

    elements.append(table)

    elements.append(PageBreak())

    # Detailed Results

    for index, result in enumerate(results, start=1):

        listening = ListeningResults.objects.filter(
            session=result
        ).first()

        reading = ReadingResults.objects.filter(
            session=result
        ).first()

        writing = WritingResults.objects.filter(
            session=result
        ).first()

        student_title = Paragraph(
            f"<b>{index}. {result.username}</b>",
            styles['Heading2']
        )

        elements.append(student_title)
        elements.append(Spacer(1, 10))

        # Listening

        if listening:

            listening_text = Paragraph(
                f"""
                <b>Listening Score:</b>
                {listening.listening_mark}
                <br/>
                <b>Correct Answers:</b>
                {listening.listening_correct_count}
                """,
                styles['BodyText']
            )

            elements.append(listening_text)
            elements.append(Spacer(1, 10))

        # Reading

        if reading:

            reading_text = Paragraph(
                f"""
                <b>Reading Score:</b>
                {reading.reading_mark}
                <br/>
                <b>Correct Answers:</b>
                {reading.reading_correct_count}
                """,
                styles['BodyText']
            )

            elements.append(reading_text)
            elements.append(Spacer(1, 10))

        # Writing

        if writing:

            writing_text = Paragraph(
                f"""
                <b>Task 1 Word Count:</b>
                {writing.task1_word_count}
                <br/>
                <b>Task 2 Word Count:</b>
                {writing.task2_word_count}
                """,
                styles['BodyText']
            )

            elements.append(writing_text)
            elements.append(Spacer(1, 10))

            task1 = Paragraph(
                f"<b>Task 1:</b><br/>{writing.task1_text}",
                styles['BodyText']
            )

            task2 = Paragraph(
                f"<b>Task 2:</b><br/>{writing.task2_text}",
                styles['BodyText']
            )

            elements.append(task1)
            elements.append(Spacer(1, 10))

            elements.append(task2)
            elements.append(Spacer(1, 20))

        elements.append(Spacer(1, 30))

    doc.build(elements)

    return response