// Copyright 2017 Google Inc. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package grumpy

import (
	"testing"
)

func TestByteArrayCompare(t *testing.T) {
	cases := []invokeTestCase{
		{args: wrapArgs(newTestByteArray(""), newTestByteArray("")), want: compareAllResultEq},
		{args: wrapArgs(newTestByteArray("foo"), newTestByteArray("foo")), want: compareAllResultEq},
		{args: wrapArgs(newTestByteArray(""), newTestByteArray("foo")), want: compareAllResultLT},
		{args: wrapArgs(newTestByteArray("foo"), newTestByteArray("")), want: compareAllResultGT},
		{args: wrapArgs(newTestByteArray("bar"), newTestByteArray("baz")), want: compareAllResultLT},
		{args: wrapArgs(newTestByteArray(""), ""), want: compareAllResultEq},
		{args: wrapArgs(newTestByteArray("foo"), "foo"), want: compareAllResultEq},
		{args: wrapArgs(newTestByteArray(""), "foo"), want: compareAllResultLT},
		{args: wrapArgs(newTestByteArray("foo"), ""), want: compareAllResultGT},
		{args: wrapArgs(newTestByteArray("bar"), "baz"), want: compareAllResultLT},
	}
	for _, cas := range cases {
		if err := runInvokeTestCase(compareAll, &cas); err != "" {
			t.Error(err)
		}
	}
}

func TestByteArrayGetItem(t *testing.T) {
	badIndexType := newTestClass("badIndex", []*Type{ObjectType}, newStringDict(map[string]*Object{
		"__index__": newBuiltinFunction("__index__", func(f *Frame, _ Args, _ KWArgs) (*Object, *BaseException) {
			return nil, f.RaiseType(ValueErrorType, "wut")
		}).ToObject(),
	}))
	cases := []invokeTestCase{
		{args: wrapArgs(newTestByteArray("bar"), 1), want: NewInt(97).ToObject()},
		{args: wrapArgs(newTestByteArray("foo"), 3.14), wantExc: mustCreateException(TypeErrorType, "bytearray indices must be integers or slice, not float")},
		{args: wrapArgs(newTestByteArray("baz"), -1), want: NewInt(122).ToObject()},
		{args: wrapArgs(newTestByteArray("baz"), -4), wantExc: mustCreateException(IndexErrorType, "index out of range")},
		{args: wrapArgs(newTestByteArray(""), 0), wantExc: mustCreateException(IndexErrorType, "index out of range")},
		{args: wrapArgs(newTestByteArray("foo"), 3), wantExc: mustCreateException(IndexErrorType, "index out of range")},
		{args: wrapArgs(newTestByteArray("bar"), newTestSlice(None, 2)), want: newTestByteArray("ba").ToObject()},
		{args: wrapArgs(newTestByteArray("bar"), newTestSlice(1, 3)), want: newTestByteArray("ar").ToObject()},
		{args: wrapArgs(newTestByteArray("bar"), newTestSlice(1, None)), want: newTestByteArray("ar").ToObject()},
		{args: wrapArgs(newTestByteArray("foobarbaz"), newTestSlice(1, 8, 2)), want: newTestByteArray("obra").ToObject()},
		{args: wrapArgs(newTestByteArray("abc"), newTestSlice(None, None, -1)), want: newTestByteArray("cba").ToObject()},
		{args: wrapArgs(newTestByteArray("bar"), newTestSlice(1, 2, 0)), wantExc: mustCreateException(ValueErrorType, "slice step cannot be zero")},
		{args: wrapArgs(newTestByteArray("123"), newObject(badIndexType)), wantExc: mustCreateException(ValueErrorType, "wut")},
	}
	for _, cas := range cases {
		if err := runInvokeMethodTestCase(ByteArrayType, "__getitem__", &cas); err != "" {
			t.Error(err)
		}
	}
}

func TestByteArrayInit(t *testing.T) {
	cases := []invokeTestCase{
		{args: wrapArgs(), want: newTestByteArray("").ToObject()},
		{args: wrapArgs(3), want: newTestByteArray("\x00\x00\x00").ToObject()},
		{args: wrapArgs([]int{3, 2, 1}), want: newTestByteArray("\x03\x02\x01").ToObject()},
		{args: wrapArgs("abc"), want: newTestByteArray("abc").ToObject()},
		{args: wrapArgs([]string{"a", "b", "c"}), want: newTestByteArray("abc").ToObject()},
		{args: wrapArgs(newTestXRange(3)), want: newTestByteArray("\x00\x01\x02").ToObject()},
		{args: wrapArgs(newTestRange(3)), want: newTestByteArray("\x00\x01\x02").ToObject()},
		{args: wrapArgs(newObject(ObjectType)), wantExc: mustCreateException(TypeErrorType, `'object' object is not iterable`)},
		{args: wrapArgs([]int{-1}), wantExc: mustCreateException(ValueErrorType, `byte must be in range(0, 256)`)},
		{args: wrapArgs([]int{256}), wantExc: mustCreateException(ValueErrorType, `byte must be in range(0, 256)`)},
		{args: wrapArgs([]string{"ab"}), wantExc: mustCreateException(ValueErrorType, `string must be of size 1`)},
		{args: wrapArgs([]interface{}{5, []interface{}{}}), wantExc: mustCreateException(TypeErrorType, `an integer or string of size 1 is required`)},
	}
	for _, cas := range cases {
		if err := runInvokeTestCase(ByteArrayType.ToObject(), &cas); err != "" {
			t.Error(err)
		}
	}
}

func TestByteArrayNative(t *testing.T) {
	val, raised := ToNative(NewRootFrame(), newTestByteArray("foo").ToObject())
	if raised != nil {
		t.Fatalf("bytearray.__native__ raised %v", raised)
	}
	data, ok := val.Interface().([]byte)
	if !ok || string(data) != "foo" {
		t.Fatalf(`bytearray.__native__() = %v, want []byte("123")`, val.Interface())
	}
}

func TestByteArrayRepr(t *testing.T) {
	cases := []invokeTestCase{
		{args: wrapArgs(newTestByteArray("")), want: NewStr("bytearray(b'')").ToObject()},
		{args: wrapArgs(newTestByteArray("foo")), want: NewStr("bytearray(b'foo')").ToObject()},
	}
	for _, cas := range cases {
		if err := runInvokeTestCase(wrapFuncForTest(Repr), &cas); err != "" {
			t.Error(err)
		}
	}
}

func TestByteArrayStr(t *testing.T) {
	cases := []invokeTestCase{
		{args: wrapArgs(newTestByteArray("")), want: NewStr("").ToObject()},
		{args: wrapArgs(newTestByteArray("foo")), want: NewStr("foo").ToObject()},
	}
	for _, cas := range cases {
		if err := runInvokeTestCase(wrapFuncForTest(ToStr), &cas); err != "" {
			t.Error(err)
		}
	}
}

func newTestByteArray(s string) *ByteArray {
	return &ByteArray{Object: Object{typ: ByteArrayType}, value: []byte(s)}
}
