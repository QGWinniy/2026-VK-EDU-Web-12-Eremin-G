let selectingAnswer = false;

document.addEventListener('submit', async (event) => {
    const form = event.target;
    if (!form.matches('[data-vote], [data-correct]')) {
        return;
    }
    event.preventDefault();
    const isVote = form.hasAttribute('data-vote');
    if (form.dataset.pending || (!isVote && selectingAnswer)) {
        return;
    }

    const data = new FormData(form, event.submitter);
    const buttons = [...form.querySelectorAll('button:not(:disabled)')];
    const error = form.querySelector('[data-error]');
    error.textContent = '';
    form.dataset.pending = 'true';
    buttons.forEach((button) => { button.disabled = true; });
    if (!isVote) {
        selectingAnswer = true;
    }

    try {
        const response = await fetch(form.action, { method: 'POST', body: data });
        const result = await response.json();
        if (!response.ok) {
            if (response.status === 401) {
                window.alert(result.error);
            }
            throw new Error(result.error);
        }
        if (isVote) {
            form.querySelector('[data-score]').textContent = result.score;
            form.querySelectorAll('button').forEach((button) => {
                button.disabled = Number(button.value) === result.value;
            });
        } else {
            document.querySelectorAll('[data-answer]').forEach((answer) => {
                const selected = answer.id === `answer-${result.answer_id}`;
                answer.querySelector('[data-correct-label]').hidden = !selected;
                answer.querySelector('[data-correct] button').disabled = selected;
            });
        }
    } catch (failure) {
        error.textContent = failure instanceof SyntaxError
            ? 'Сервер не вернул результат операции.'
            : failure.message;
        buttons.forEach((button) => { button.disabled = false; });
    } finally {
        delete form.dataset.pending;
        if (!isVote) {
            selectingAnswer = false;
        }
    }
});
