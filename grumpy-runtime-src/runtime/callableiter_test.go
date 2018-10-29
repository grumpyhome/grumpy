// Copyright 2018 Google Inc. All Rights Reserved.
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

func TestCallableIterator(t *testing.T) {
	fun := newBuiltinFunction("TestCallableIterator", func(f *Frame, args Args, _ KWArgs) (*Object, *BaseException) {
		return TupleType.Call(f, args, nil)
	}).ToObject()
	makeCounter := func() *Object {
		cnt := 0
		return newBuiltinFunction("counter", func(f *Frame, _ Args, _ KWArgs) (*Object, *BaseException) {
			cnt++
			return NewInt(cnt).ToObject(), nil
		}).ToObject()
	}
	exhaustedIter := newCallableIterator(makeCounter(), NewInt(2).ToObject())
	TupleType.Call(NewRootFrame(), []*Object{exhaustedIter}, nil)
	cases := []invokeTestCase{
		{args: wrapArgs(newCallableIterator(makeCounter(), NewInt(4).ToObject())), want: newTestTuple(1, 2, 3).ToObject()},
		{args: wrapArgs(newCallableIterator(makeCounter(), NewInt(1).ToObject())), want: newTestTuple().ToObject()},
		{args: wrapArgs(exhaustedIter), want: NewTuple().ToObject()},
	}
	for _, cas := range cases {
		if err := runInvokeTestCase(fun, &cas); err != "" {
			t.Error(err)
		}
	}
}
