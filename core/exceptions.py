import re

import fastapi as fa
import openpyxl
from sqlalchemy.exc import IntegrityError

from database.models.link import LinkModel
from database.models.user import UserModel
from services.notificator.notificator import Notificator

UnauthorizedException = fa.HTTPException(
    status_code=fa.status.HTTP_401_UNAUTHORIZED,
    detail="Not authorized",
)

NotExcelException = fa.HTTPException(
    status_code=fa.status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail={'validation_errors': ['File should be Microsoft Excel .xslx spreadsheet']}
)


class LinkAlreadyExistsException(fa.HTTPException):

    def __init__(self, error: IntegrityError | LinkModel):
        if isinstance(error, IntegrityError):
            super().__init__(
                status_code=fa.status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error.orig.diag.message_detail
            )
        elif isinstance(error, LinkModel):
            link_url = error.link_url
            page_url = error.page_url
            anchor = error.anchor

            super().__init__(
                status_code=fa.status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f'link with {link_url=:}, {page_url=:}, {anchor=:} already exists.')
        else:
            raise ValueError


class LinkAlreadyExistsFromFileException(fa.HTTPException):

    @staticmethod
    def get_row_numbers_str(filepath, link_url, page_url, anchor, from_archive=False) -> str:
        row_numbers = []
        try:
            wb = openpyxl.load_workbook(filename=filepath)
        except KeyError:
            raise NotExcelException
        ws = wb.active

        for num, row in enumerate(ws.iter_rows(), start=1):
            row_list = [cell.value for cell in row[:8]]
            if from_archive:
                r_created_at, r_link_url, r_anchor, r_page_url, *the_rest = row_list
            else:
                r_page_url, r_link_url, r_anchor, *the_rest = row_list
            if r_page_url == page_url and r_link_url == link_url and r_anchor == anchor:
                row_numbers.append(str(num))

        return ', '.join(row_numbers)

    def __init__(self, filepath, error: IntegrityError, from_archive=False):
        validation_errors = []

        if isinstance(error.params, dict):
            link_url = error.params.get('link_url')
            page_url = error.params.get('page_url')
            anchor = error.params.get('anchor')

        elif isinstance(error.params, tuple):
            message_detail = error.orig.diag.message_detail
            link_values = [_.strip() for _ in
                           re.search(pattern=r"(?:=\()(.*)(?:\))", string=message_detail).group(1).split(',')]
            link_order = [_.strip() for _ in
                          re.search(pattern=r"(?:\()(.*)(?:\)=)", string=message_detail).group(1).split(',')]

            link_url = link_values[link_order.index('link_url')]
            page_url = link_values[link_order.index('page_url')]
            anchor = link_values[link_order.index('anchor')]
        else:
            raise ValueError('in LinkAlreadyExistsFromFileException error.params nor dict, nor tuple')

        row_number = self.get_row_numbers_str(filepath, link_url, page_url, anchor, from_archive)
        if from_archive:
            validation_errors.append(
                f'error at row number {row_number}: link with {page_url=:}, {anchor=:}, {link_url=:} has duplicates in file'
            )
        else:
            validation_errors.append(
                f'error at row number {row_number}: link with {page_url=:}, {anchor=:}, {link_url=:} already exists.'
            )
        super().__init__(
            status_code=fa.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={'validation_errors': validation_errors})


class WhileUploadingArchiveException(Exception):
    def __init__(self, message, errors: list[str], user: UserModel):
        super().__init__(message)
        with Notificator() as notificator:
            errors_text = 'errors while uploading link archive: \n\n{0}'.format('\n'.join(errors))
            notificator.send_email(user, text=errors_text)
            notificator.send_message(user, text=errors_text)

            errors_chunk = []
            while errors:
                error = errors.pop()
                errors_chunk.append(error)
                if len(errors_chunk) == 15 or len(errors) == 0:
                    notificator.send_telegram(user, text=str('\n'.join(errors_chunk)))
                    errors_chunk = []


class CheckWithPlaywrightException(Exception):
    def __init__(self, message, response_code):
        super().__init__(message)
        self.response_code = response_code


class AcceptorNotFoundException(Exception):
    def __init__(self, message, response_code):
        super().__init__(message)
        self.response_code = response_code
