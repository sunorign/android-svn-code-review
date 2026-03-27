from src.local_rules.android_rules.viewholder_pattern import ViewHolderPatternRule
from src.diff_parser import FileDiff, DiffChange


def test_finds_findviewbyid_in_getview():
    rule = ViewHolderPatternRule()
    change = DiffChange(line_number=10, content='        TextView textView = findViewById(R.id.text_view);', is_added=True, is_removed=False)
    file_diff = FileDiff("MyAdapter.java", False, False)
    findings = rule.check_diff(file_diff, change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert "findViewById call detected" in findings[0].message


def test_finds_findviewbyid_in_onbindviewholder():
    rule = ViewHolderPatternRule()
    change = DiffChange(line_number=10, content='        ImageView imageView = findViewById(R.id.image_view);', is_added=True, is_removed=False)
    file_diff = FileDiff("MyRecyclerViewAdapter.java", False, False)
    findings = rule.check_diff(file_diff, change)

    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert "findViewById call detected" in findings[0].message


def test_ignores_findviewbyid_in_non_adapter():
    rule = ViewHolderPatternRule()
    change = DiffChange(line_number=10, content='        TextView textView = findViewById(R.id.text_view);', is_added=True, is_removed=False)
    file_diff = FileDiff("MainActivity.java", False, False)
    findings = rule.check_diff(file_diff, change)

    assert len(findings) == 0


def test_ignores_comments():
    rule = ViewHolderPatternRule()
    change = DiffChange(line_number=10, content='        // TextView textView = findViewById(R.id.text_view);', is_added=True, is_removed=False)
    file_diff = FileDiff("MyAdapter.java", False, False)
    findings = rule.check_diff(file_diff, change)

    assert len(findings) == 0


def test_check_full_file_in_getview():
    rule = ViewHolderPatternRule()
    file_content = """
    public class MyAdapter extends ArrayAdapter<String> {
        public View getView(int position, View convertView, ViewGroup parent) {
            View view = LayoutInflater.from(context).inflate(R.layout.item, parent, false);
            TextView textView = findViewById(R.id.text_view);
            ImageView imageView = findViewById(R.id.image_view);
            textView.setText(getItem(position));
            return view;
        }
    }
    """
    findings = rule.check_full_file("MyAdapter.java", file_content)

    assert len(findings) == 2
    assert all(f.severity == "WARNING" for f in findings)
    assert all("findViewById" in f.message for f in findings)


def test_check_full_file_in_onbindviewholder():
    rule = ViewHolderPatternRule()
    file_content = """
    public class MyViewHolder extends RecyclerView.ViewHolder {
        TextView textView;
        ImageView imageView;

        public MyViewHolder(View itemView) {
            super(itemView);
            textView = itemView.findViewById(R.id.text_view);
            imageView = itemView.findViewById(R.id.image_view);
        }
    }

    public class MyAdapter extends RecyclerView.Adapter<MyViewHolder> {
        public void onBindViewHolder(MyViewHolder holder, int position) {
            TextView text = findViewById(R.id.text_view);
            text.setText(items[position]);
        }
    }
    """
    findings = rule.check_full_file("MyRecyclerViewAdapter.java", file_content)

    # 只有 onBindViewHolder 中的 findViewById 会被标记
    assert len(findings) == 1
    assert findings[0].severity == "WARNING"
    assert "findViewById call in getView()/onBindViewHolder()" in findings[0].message
