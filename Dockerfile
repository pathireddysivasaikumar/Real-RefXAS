FROM python:3.9.0

RUN pip install --upgrade pip

RUN mkdir -p /raw_data_files

COPY . /app
WORKDIR /app

RUN mkdir -p /app/temp /app/pip_cache

# pymatgen==2023.1.30's Cython extensions (e.g. cdef int = 3 ** n_pbc) don't
# compile under Cython 3.x's stricter type inference; pin pre-3.0 for the build.
RUN echo "Cython<3.0" > /tmp/build-constraints.txt
ENV PIP_CONSTRAINT=/tmp/build-constraints.txt
RUN pip install "Cython<3.0" "setuptools<66"

RUN pip install -e . --cache-dir /app/pip_cache
RUN pip install -r requirements.txt --cache-dir /app/pip_cache --ignore-installed

EXPOSE 8000
