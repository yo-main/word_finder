#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-


import sys
import os
import argparse

ACCEPTED_FORMAT = (".py", ".html", ".js", ".txt", ".log", ".php")


class Finder(object):
    log_file = "logs.txt"

    size_title = 0
    size_row = 0

    def __init__(self):

        self.build_parser()
        self.parse_arguments()

        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def run(self):
        for filepath in self.get_file():
            if not self.filename:
                self.search_file_content(filepath)
            else:
                self.search_filename(filepath)

        if not self.filename:
            self.print_result()

    def search_filename(self, filepath):
        filename = os.path.basename(filepath)

        for word in self.words:
            if word in filename.encode():
                print(filepath)

    def _prepare_printing(self):
        out = []
        total = {word: 0 for word in self.words}

        title_words = tuple(word.decode() for word in self.words)
        out.append(("FILE",) + title_words)

        self.size_row = len(max(title_words, key=len))
        self.size_title = len(out[0][0])

        for filepath in self.words_count:
            row = [
                str(self.words_count[filepath][word]) for word in self.words
            ]
            row.insert(0, filepath)

            for word in self.words:
                total[word] += self.words_count[filepath][word]

            self.size_title = max(self.size_title, len(filepath))
            self.size_row = max(self.size_row, len(max(row[1:], key=len)))

            out.append(row)

        if len(out) > 2:
            total_row = [str(total[word]) for word in self.words]
            total_row.insert(0, "TOTAL")
            out.append(total_row)

        return out

    def print_result(self):
        if not self.words_count:
            print("No result found !")
            return False

        to_print = self._prepare_printing()

        template = "{filepath:<{max_size_filepath}}"
        template += " | {:>{max_size_word}}" * len(self.words)

        for row in to_print:
            print(
                template.format(
                    filepath=row[0],
                    max_size_filepath=self.size_title,
                    max_size_word=self.size_row,
                    *row[1:]
                )
            )

    def _is_file_searchable(self, filename):
        if filename.startswith("."):
            return False
        if not self.all_files and not any(
            filename.endswith(ext) for ext in ACCEPTED_FORMAT
        ):
            return False
        return True

    def get_file(self):
        for root, dirs, files in os.walk(self.directory):
            dirs = [dir_ for dir_ in dirs if not dir_.startswith(".")]
            for filename in files:
                if not self._is_file_searchable(filename):
                    continue
                filepath = os.path.join(root, filename)
                yield filepath

    def search_file_content(self, filepath):
        with open(filepath, "rb") as f:
            row_nb = 0
            for row in f.readlines():
                row_nb += 1

                if self.search_row(row, filepath):
                    self.match_found(filepath, row, row_nb)

    def search_row(self, row, filepath):
        word_found = False
        words_checked = []
        row_counter = {}

        if self.case_sensitive:
            row = row.lower()

        for excluded_word in self.excluded:
            if excluded_word in row:
                return False

        for word in self.words:
            count = row.count(word)

            max_ref = 0
            for past_word in words_checked:
                if word in past_word:
                    max_ref = max(max_ref, row.count(past_word))
            count -= max_ref

            row_counter[word] = max(count, 0)
            if count:
                word_found = True

            words_checked.append(word)

        if word_found:
            self._register_row_counter(filepath, row_counter)
            return True

        return False

    def _register_row_counter(self, filepath, counter):
        if self.full_path:
            filename = filepath
        else:
            filename = os.path.basename(filepath)

        if filename not in self.words_count:
            self.words_count[filename] = {word: 0 for word in self.words}

        for word, count in counter.items():
            self.words_count[filename][word] += count

    def match_found(self, filepath, row, row_nb):
        template = "Match found on row {}\n{}\n{}\n\n".format(
            row_nb, filepath, row.decode(errors="replace")
        )

        if self.verbose:
            print(template)
        if self.save:
            with open(self.log_file, "a") as f:
                f.write(template)

    def parse_arguments(self):
        arguments = sys.argv[1:]
        res = self.parser.parse_args(arguments)
        self.original_words = res.words
        self.verbose = res.verbose
        self.directory = res.directory
        self.full_path = res.full_path
        self.filename = res.name
        self.case_sensitive = res.case_sensitive
        self.save = res.save
        self.all_files = res.all_files
        self.excluded = res.exclude or []
        self.excluded = [word.encode() for word in self.excluded]
        self.words = [word.encode() for word in self.original_words]
        self.words = sorted(self.words, key=len, reverse=True)

        if self.case_sensitive:
            self.words = [word.lower() for word in self.words]
            self.excluded = [word.lower() for word in self.excluded]

        self.words_count = {}

    def build_parser(self):
        description = "Look for match in indicated folder"

        self.parser = argparse.ArgumentParser(description=description)

        self.parser.add_argument(
            "words", nargs="+", help="word(s) that you are looking for"
        )
        self.parser.add_argument(
            "-dir",
            "--directory",
            default=".",
            help="folder in which to make the search " "(recursive)",
        )
        self.parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="print the row where a match is hit",
        )
        self.parser.add_argument(
            "-fp",
            "--full_path",
            action="store_true",
            help="show full filepath instead of just the file name",
        )
        self.parser.add_argument(
            "-cs",
            "--case_sensitive",
            action="store_false",
            help="search is case sensitive",
        )
        self.parser.add_argument(
            "-s",
            "--save",
            action="store_true",
            help="save search details result in a file from your current directory",
        )
        self.parser.add_argument(
            "-n",
            "--name",
            action="store_true",
            help="search by filename instead of content",
        )
        self.parser.add_argument(
            "-a",
            "--all_files",
            action="store_true",
            help="will look through all files extentions",
        )
        self.parser.add_argument(
            "-e",
            "--exclude",
            nargs="*",
            help="Will not match any line with one of the provided keyword",
        )


if __name__ == "__main__":
    finder = Finder()
    finder.run()
