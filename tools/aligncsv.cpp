#include <cerrno>
#include <cstdio>
#include <cstddef>

#include <unistd.h>

#include <vector>
#include <string>

// this configuration puts 2-5 spaces between entries (excluding headers)
// and rounds the start of each field up to 4, for easier manual indenting
// but force each field to be at least size 8
const size_t min_pad = 2;
const size_t align_pad = 4;
const size_t min_size = 8;

void add_pieces(std::vector<std::string>& line, std::vector<size_t>& sizes)
{
    // This would get rid of trailing commas,
    // but that would break certain db.txt files.
    // Instead we'll have to manually check whether it's empty when checking length
//     if (!line.empty() && line.back().empty())
//         line.pop_back();
    size_t num_sizes = line.size();
    if (!num_sizes) // line.empty()
        return;
    if (line[0].size() >= 2
        && (line[0][0] == '#'
            || (line[0][0] == '/'
                && line[0][1] == '/')))
        return;

    if (num_sizes > sizes.size())
        sizes.resize(num_sizes, 1UL);
    for (size_t i = 0; i < num_sizes; ++i)
    {
        size_t elt_size = line[i].size();
        if (!elt_size)// line[i].empty()
            continue;
        if (line[i][elt_size - 1] == ' ')
            line[i].resize(--elt_size);
        // mandatory padding and comma
        elt_size += min_pad + 1;
        if (elt_size < min_size)
            elt_size = min_size;
        if (elt_size > sizes[i])
            // always true if we expanded sizes
            sizes[i] = elt_size;
    }
}

// the arguments may be the same file - the whole file is stored in memory
void aligncsv(FILE *in, FILE *out, const char *name)
{
    bool newline = true;
    bool can_split = true;
    bool can_have_whitespace = false;
    int c;
    std::vector<std::vector<std::string> > contents;

    while ((c = fgetc(in)) != -1)
    {
        if (c == '}' || c == '\n')
            can_split = true;
        if (c == '\n')
        {
            if (newline)
            {
                // preserve consecutive blank lines
                contents.push_back(std::vector<std::string>());
            }
            newline = true;
            continue;
        }
        if (c == '{')
            can_split = false;
        if (c == '\t')
            c = ' ';
        if (c == ' ')
        {
            if (!can_have_whitespace)
                continue;
            can_have_whitespace = false;
        }
        else
            can_have_whitespace = true;
        if (newline)
        {
            contents.push_back(std::vector<std::string>(1, std::string(1, c)));
            newline = false;
        }
        else
        {
            if (can_split && c == ',')
            {
                can_have_whitespace = false;
                contents.back().push_back(std::string());
            }
            else
                contents.back().back() += c;
        }
    }

    typedef std::vector<std::vector<std::string> >::iterator outer_it;
    typedef std::vector<std::vector<std::string> >::const_iterator outer_cit;
    typedef std::vector<size_t>::iterator pieces_it;
    // at this point, each entry in a line:
    // * does not start with whitespace
    // * has one space in place of any previous run of whitespace
    // * may end in a single space
    // The last is fixed during add_pieces
    std::vector<size_t> pieces;
    for (outer_it it = contents.begin(), end = contents.end(); it != end; ++it)
        add_pieces(*it, pieces);
    for (pieces_it it = pieces.begin(), end = pieces.end(); it != end; ++it)
        if (size_t trail = *it % align_pad)
            *it += align_pad - trail;

    if (in == out)
    {
        //rewind(out);
        if (fseek(out, 0, SEEK_SET) == -1)
        {
            perror(name);
            return;
        }
        if (ftruncate(fileno(out), 0) == -1)
        {
            perror(name);
            return;
        }
    }
    for (outer_cit oit = contents.begin(), oend = contents.end(); oit != oend; ++oit)
    {
        const std::vector<std::string>& inner = *oit;
        size_t num_elems = inner.size();
        // we have previously guaranteed that pieces[i].size() >= num_elems
        for (size_t i = 0; i < num_elems; ++i)
        {
            // FIXME handle UTF-8 characters (here AND above?)
            if (fputs(inner[i].c_str(), out) == -1)
            {
                perror(name);
                return;
            }
            if (i != num_elems - 1)
            {
                if (fputc(',', out) == -1)
                {
                    perror(name);
                    return;
                }
                size_t elem_length = inner[i].size() + 1;
                while (elem_length++ < pieces[i])
                {
                    if (fputc(' ', out) == -1)
                    {
                        perror(name);
                        return;
                    }
                }
            }
        }
        fputc('\n', out);
    }
}

int main(int argc, char **argv)
{
    if (argc == 1)
        aligncsv(stdin, stdout, "<stdio>");
    for (int i = 1; i < argc; ++i)
    {
        FILE *f = fopen(argv[i], "r+");
        if (!f)
        {
            perror(argv[i]);
            continue;
        }
        aligncsv(f, f, argv[i]);
        fclose(f);
    }
}
